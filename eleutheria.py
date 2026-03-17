import asyncio
import websockets
import json
import hmac
import hashlib
import requests
import time
import logging
from urllib.parse import urlparse
from decimal import Decimal, ROUND_DOWN
from config import *

# Configuration du Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("eleutheria_ws.log"), logging.StreamHandler()])
logger = logging.getLogger("eleutheria")

class EleutheriaHFT:
    def __init__(self):
        self.prix_entree = 0
        self.prix_max_atteint = 0
        self.en_position = False
        self.pertes_du_jour = 0.0
        self.quantite_en_possession = 0.0  # Mémorisation exacte de la quantité achetée
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.verrou = asyncio.Lock()       # Cadenas anti-double ordre

    def signer(self, method, request_path, body=""):
        # Nouvelle méthode de signature Coinbase (sans Passphrase, Timestamp entier)
        timestamp = str(int(time.time()))
        message = timestamp + method + request_path + str(body)
        
        # Encodage du secret et création de la signature
        signature = hmac.new(
            API_SECRET.encode('utf-8'), 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        return {
            "CB-ACCESS-KEY": API_KEY,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }

    def passer_ordre(self, cote, quantite):
        logger.warning(f"⚠️ [LIVE] Envoi de l'ordre {cote.upper()} de {quantite} HBAR à Coinbase...")
        
        # Préparation de l'ordre
        ordre = {"side": cote, "product_id": HBAR_SYMBOL, "type": "market", "size": str(quantite)}
        body = json.dumps(ordre)
        
        # Construction de l'URL finale et extraction du chemin pour la signature
        endpoint_url = f"{API_URL}/orders"
        request_path = urlparse(endpoint_url).path
        
        headers = self.signer("POST", request_path, body)
        
        try:
            # Envoi avec un timeout de 5 secondes pour éviter de bloquer le bot
            r = requests.post(endpoint_url, headers=headers, data=body, timeout=5)
            
            if r.status_code in [200, 201]:
                logger.info(f"✅ Ordre {cote.upper()} exécuté avec succès.")
                return True
            else:
                logger.error(f"❌ Échec de l'ordre : {r.text}")
                return False
        except Exception as e:
            logger.error(f"⚠️ Erreur réseau lors de l'envoi de l'ordre : {e}")
            return False

    async def traiter_prix(self, prix, volume_24h):
        # On verrouille le traitement pour éviter les collisions si les prix arrivent trop vite
        async with self.verrou:
            
            # Vérification du coupe-circuit (basé sur la config en EUR)
            if self.pertes_du_jour >= PERTE_MAX_JOURNALIERE_EUR:
                return

            if not self.en_position:
                # Filtre de volume pour éviter les marchés morts
                if float(volume_24h) < 50000:
                    return 

                if PRIX_ACHAT_MIN <= prix <= PRIX_ACHAT_MAX:
                    # Calcul propre de la quantité
                    quantite = float(Decimal(MONTANT_ACHAT / prix).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
                    
                    if self.passer_ordre("buy", quantite):
                        self.prix_entree = prix
                        self.prix_max_atteint = prix
                        self.en_position = True
                        self.quantite_en_possession = quantite # On sauvegarde la quantité exacte
                        logger.info(f"🚀 ACHAT IMMÉDIAT à {prix}€")
            else:
                # Mise à jour du sommet atteint
                if prix > self.prix_max_atteint:
                    self.prix_max_atteint = prix
                
                profit = (prix - self.prix_entree) / self.prix_entree
                baisse = (self.prix_max_atteint - prix) / self.prix_max_atteint

                doit_vendre = False
                
                # SÉCURITÉ : Hard Stop Loss
                if profit <= -HARD_STOP_LOSS:
                    logger.warning("🚨 STOP LOSS DÉCLENCHÉ !")
                    doit_vendre = True
                    self.pertes_du_jour += MONTANT_ACHAT * abs(profit)
                    
                # GAIN : Trailing Stop
                elif profit >= PROFIT_MIN_POUR_SUIVI and baisse >= DISTANCE_TRAILING_STOP:
                    logger.info("💰 PRISE DE PROFIT OPTIMISÉE")
                    doit_vendre = True

                if doit_vendre:
                    # On revend exactement ce qu'on a acheté
                    if self.passer_ordre("sell", self.quantite_en_possession):
                        self.en_position = False
                        self.quantite_en_possession = 0.0 # Remise à zéro
                        logger.info(f"✅ VENTE à {prix}€ | Gain/Perte géré.")

    async def ecouter_marche(self):
        logger.info("⚡ Connexion WebSocket Coinbase en cours...")
        subscribe_message = {
            "type": "subscribe",
            "product_ids": [HBAR_SYMBOL],
            "channels": ["ticker"]
        }

        # Boucle de reconnexion automatique en cas de micro-coupure internet
        while True: 
            try:
                async with websockets.connect(self.ws_url) as ws:
                    await ws.send(json.dumps(subscribe_message))
                    logger.info("📡 Flux temps réel activé. Le bot surveille le marché...")

                    while True:
                        reponse = await ws.recv()
                        data = json.loads(reponse)
                        
                        if data["type"] == "ticker" and "price" in data:
                            # asyncio.create_task lance le traitement sans bloquer la réception du flux
                            asyncio.create_task(self.traiter_prix(float(data["price"]), float(data["volume_24h"])))
                            
            except Exception as e:
                logger.error(f"Erreur WebSocket : {e}. Reconnexion dans 5 secondes...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    bot = EleutheriaHFT()
    asyncio.run(bot.ecouter_marche())