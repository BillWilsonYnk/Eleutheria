import asyncio
import websockets
import json
import hmac
import hashlib
import requests
import base64
import datetime
import logging
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
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"

    def signer(self, method, endpoint, body=""):
        timestamp = str(datetime.datetime.utcnow().timestamp())
        message = timestamp + method + endpoint + body
        key = base64.b64decode(API_SECRET)
        signature = hmac.new(key, message.encode('utf-8'), hashlib.sha256)
        return {
            "CB-ACCESS-KEY": API_KEY,
            "CB-ACCESS-SIGN": base64.b64encode(signature.digest()).decode('utf-8'),
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": API_PASSPHRASE,
            "Content-Type": "application/json"
        }

    def passer_ordre(self, cote, quantite):
        # --- MODE RÉEL ACTIVÉ ---
        logger.warning(f"⚠️ [LIVE] Envoi de l'ordre {cote.upper()} de {quantite} HBAR à Coinbase...")
        ordre = {"side": cote, "product_id": HBAR_SYMBOL, "type": "market", "size": str(quantite)}
        body = json.dumps(ordre)
        headers = self.signer("POST", "/orders", body)
        r = requests.post(f"{API_URL}/orders", headers=headers, data=body)
        
        if r.status_code in [200, 201]:
            logger.info(f"✅ Ordre {cote.upper()} exécuté avec succès par Coinbase.")
            return True
        else:
            logger.error(f"❌ Échec de l'ordre : {r.text}")
            return False

    async def traiter_prix(self, prix, volume_24h):
        if self.pertes_du_jour >= PERTE_MAX_JOURNALIERE_USD:
            return

        if not self.en_position:
            if float(volume_24h) < 1000000:
                return 

            if PRIX_ACHAT_MIN <= prix <= PRIX_ACHAT_MAX:
                quantite = float(Decimal(MONTANT_ACHAT / prix).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
                if self.passer_ordre("buy", quantite):
                    self.prix_entree = prix
                    self.prix_max_atteint = prix
                    self.en_position = True
                    logger.info(f"🚀 ACHAT IMMÉDIAT à {prix}€")
        else:
            if prix > self.prix_max_atteint:
                self.prix_max_atteint = prix
            
            profit = (prix - self.prix_entree) / self.prix_entree
            baisse = (self.prix_max_atteint - prix) / self.prix_max_atteint

            doit_vendre = False
            
            if profit <= -HARD_STOP_LOSS:
                logger.warning("🚨 STOP LOSS DÉCLENCHÉ !")
                doit_vendre = True
                self.pertes_du_jour += MONTANT_ACHAT * abs(profit)
                
            elif profit >= PROFIT_MIN_POUR_SUIVI and baisse >= DISTANCE_TRAILING_STOP:
                logger.info("💰 PRISE DE PROFIT OPTIMISÉE")
                doit_vendre = True

            if doit_vendre:
                quantite_vendre = float(Decimal(MONTANT_ACHAT / self.prix_entree).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
                if self.passer_ordre("sell", quantite_vendre):
                    self.en_position = False
                    logger.info(f"✅ VENTE à {prix}€ | Gain/Perte géré.")

    async def ecouter_marche(self):
        logger.info("⚡ Connexion WebSocket Coinbase en cours...")
        subscribe_message = {
            "type": "subscribe",
            "product_ids": [HBAR_SYMBOL],
            "channels": ["ticker"]
        }

        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps(subscribe_message))
            logger.info("📡 Flux temps réel activé. Le bot surveille le marché...")

            while True:
                try:
                    reponse = await ws.recv()
                    data = json.loads(reponse)
                    
                    if data["type"] == "ticker" and "price" in data:
                        await self.traiter_prix(float(data["price"]), float(data["volume_24h"]))
                        
                except Exception as e:
                    logger.error(f"Erreur : {e}")
                    await asyncio.sleep(5)

if __name__ == "__main__":
    bot = EleutheriaHFT()
    asyncio.run(bot.ecouter_marche())
