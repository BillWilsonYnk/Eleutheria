import time
import json
import hmac
import hashlib
import requests
import base64
import datetime
import logging
from decimal import Decimal, ROUND_DOWN
from config import (
    API_KEY,
    API_SECRET,
    API_PASSPHRASE,
    API_URL,
    HBAR_SYMBOL,
    MONTANT_ACHAT,
    INTERVALLE_VERIFICATION,
    PRIX_ACHAT_MIN,
    PRIX_ACHAT_MAX,
    HARD_STOP_LOSS,
    PROFIT_MIN_POUR_SUIVI,
    DISTANCE_TRAILING_STOP,
    DRY_RUN,
)

# Logging ultra-clair
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("eleutheria_trading.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("eleutheria")


class EleutheriaBot:
    def __init__(self):
        self.prix_entree = 0.0
        self.prix_max_atteint = 0.0
        self.en_position = False
        self.quantite_position = 0.0

    def signer(self, method: str, endpoint: str, body: str = "") -> dict:
        timestamp = str(datetime.datetime.utcnow().timestamp())
        message = timestamp + method + endpoint + body
        key = base64.b64decode(API_SECRET)
        signature = hmac.new(key, message.encode("utf-8"), hashlib.sha256)
        return {
            "CB-ACCESS-KEY": API_KEY,
            "CB-ACCESS-SIGN": base64.b64encode(signature.digest()).decode("utf-8"),
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": API_PASSPHRASE,
            "Content-Type": "application/json",
        }

    def obtenir_prix(self) -> float | None:
        try:
            r = requests.get(f"{API_URL}/products/{HBAR_SYMBOL}/ticker", timeout=10)
            r.raise_for_status()
            data = r.json()
            prix = float(data["price"])
            return prix
        except Exception as e:
            logger.exception(f"Erreur lors de la récupération du prix: {e}")
            return None

    def passer_ordre(self, cote: str, quantite: float) -> bool:
        """Envoie un ordre de marché. En mode DRY_RUN, ne fait que logguer."""
        if quantite <= 0:
            logger.warning("Quantité <= 0, ordre ignoré.")
            return False

        ordre = {
            "side": cote,
            "product_id": HBAR_SYMBOL,
            "type": "market",
            "size": str(quantite),
        }

        if DRY_RUN:
            logger.info(f"[DRY_RUN] Ordre simulé: {ordre}")
            return True

        body = json.dumps(ordre)
        headers = self.signer("POST", "/orders", body)

        try:
            r = requests.post(
                f"{API_URL}/orders", headers=headers, data=body, timeout=10
            )
            if r.status_code not in (200, 201):
                logger.error(
                    f"Échec envoi ordre {cote} {quantite} HBAR - "
                    f"Status: {r.status_code}, Réponse: {r.text}"
                )
                return False

            try:
                data = r.json()
                order_id = data.get("id", "inconnu")
                status = data.get("status", "inconnu")
                logger.info(
                    f"Ordre {cote} {quantite} HBAR envoyé avec succès - "
                    f"id={order_id}, status={status}"
                )
            except Exception:
                logger.info(
                    f"Ordre {cote} {quantite} HBAR envoyé avec succès "
                    f"(impossible de parser la réponse JSON)"
                )

            return True
        except Exception as e:
            logger.exception(f"Erreur lors de l'envoi de l'ordre: {e}")
            return False

    def executer(self):
        logger.info(
            f"⚡ Démarrage Eleutheria Pro "
            f"(DRY_RUN={'ON' if DRY_RUN else 'OFF'})"
        )
        while True:
            try:
                prix = self.obtenir_prix()
                if prix is None:
                    time.sleep(INTERVALLE_VERIFICATION)
                    continue

                if not self.en_position:
                    # Logique d'achat
                    if PRIX_ACHAT_MIN <= prix <= PRIX_ACHAT_MAX:
                        quantite = float(
                            Decimal(MONTANT_ACHAT / prix).quantize(
                                Decimal("0.01"), rounding=ROUND_DOWN
                            )
                        )
                        if self.passer_ordre("buy", quantite):
                            self.prix_entree = prix
                            self.prix_max_atteint = prix
                            self.en_position = True
                            self.quantite_position = quantite
                            logger.info(f"🛒 ACHAT à {prix}$ pour {quantite} HBAR")
                else:
                    # Logique de Trailing Stop
                    if prix > self.prix_max_atteint:
                        self.prix_max_atteint = prix

                    profit = (prix - self.prix_entree) / self.prix_entree
                    baisse = (
                        (self.prix_max_atteint - prix) / self.prix_max_atteint
                        if self.prix_max_atteint > 0
                        else 0
                    )

                    logger.info(
                        f"Prix actuel: {prix}$ | Entrée: {self.prix_entree}$ | "
                        f"Plus haut: {self.prix_max_atteint}$ | "
                        f"Profit: {profit*100:.2f}% | Baisse depuis le plus haut: {baisse*100:.2f}%"
                    )

                    # Sortie : soit Stop Loss, soit Trailing Stop après profit
                    doit_vendre = False
                    if profit <= -HARD_STOP_LOSS:
                        logger.warning("🚨 STOP LOSS déclenché !")
                        doit_vendre = True
                    elif profit >= PROFIT_MIN_POUR_SUIVI and baisse >= DISTANCE_TRAILING_STOP:
                        logger.info("💰 TRAILING STOP déclenché, prise de profit !")
                        doit_vendre = True

                    if doit_vendre:
                        quantite_vendre = float(
                            Decimal(self.quantite_position).quantize(
                                Decimal("0.01"), rounding=ROUND_DOWN
                            )
                        )
                        if self.passer_ordre("sell", quantite_vendre):
                            logger.info(f"✅ VENTE à {prix}$ pour {quantite_vendre} HBAR")
                            self.en_position = False
                            self.quantite_position = 0.0
                            self.prix_entree = 0.0
                            self.prix_max_atteint = 0.0

                time.sleep(INTERVALLE_VERIFICATION)
            except Exception as e:
                logger.exception(f"Erreur inattendue dans la boucle principale: {e}")
                # Petit backoff pour éviter une boucle d'erreurs serrée
                time.sleep(5)


if __name__ == "__main__":
    bot = EleutheriaBot()
    bot.executer()
