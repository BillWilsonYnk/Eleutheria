# --- CONFIGURATION ELEUTHERIA PRO (MODE LIVE) ---

API_KEY = "VOTRE_API_KEY"
API_SECRET = "VOTRE_API_SECRET" # Toujours faire attention aux '=' à la fin
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"

API_URL = "https://api.exchange.coinbase.com"
HBAR_SYMBOL = "HBAR-EUR"  # Modifié pour trader avec tes Euros

# --- PARAMÈTRES ---
MONTANT_ACHAT = 10000        
PRIX_ACHAT_MIN = 0.0800
PRIX_ACHAT_MAX = 0.1800

# --- SÉCURITÉ ---
HARD_STOP_LOSS = 0.005 # -0.5% (Risque 50€ max)
PERTE_MAX_JOURNALIERE_USD = 100 # Coupe-circuit

# --- STRATÉGIE ---
PROFIT_MIN_POUR_SUIVI = 0.007 # Sécurise à +0.7%
DISTANCE_TRAILING_STOP = 0.003 # Vend à -0.3% du sommet