"""
Configuration Eleutheria Pro (MODE LIVE)

⚠️ IMPORTANT: ne commit jamais tes clés API.
Renseigne-les via variables d’environnement :

- COINBASE_API_KEY
- COINBASE_API_SECRET
"""

import os


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Create a .env (not committed) or export it in your shell."
        )
    return value


API_KEY = _require_env("COINBASE_API_KEY")
API_SECRET = _require_env("COINBASE_API_SECRET")

API_URL = "https://api.coinbase.com/api/v3/brokerage"
HBAR_SYMBOL = "HBAR-EUR"  # Modifié pour trader avec tes Euros

# --- PARAMÈTRES ---
MONTANT_ACHAT = 50       
PRIX_ACHAT_MIN = 0.0800
PRIX_ACHAT_MAX = 0.1800

# --- SÉCURITÉ ---
HARD_STOP_LOSS = 0.005 # Toujours -0.5% (Risque : 0,25 € par trade)
PERTE_MAX_JOURNALIERE_EUR = 2 # Le bot s'arrête s'il perd 2 € dans la journée

# --- STRATÉGIE ---
PROFIT_MIN_POUR_SUIVI = 0.007 # Sécurise à +0.7%
DISTANCE_TRAILING_STOP = 0.003 # Vend à -0.3% du sommet