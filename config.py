# Configuration simple pour Eleutheria Trading Bot

# Clés API Coinbase (à remplacer par vos vraies clés)
API_KEY = "VOTRE_API_KEY"
API_SECRET = "VOTRE_API_SECRET"
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"

# Configuration de l'API
API_URL = "https://api.exchange.coinbase.com"
HBAR_SYMBOL = "HBAR-USD"

# Paramètres de trading
MONTANT_ACHAT = 100  # Montant fixe à acheter en USD
INTERVALLE_VERIFICATION = 1800  # 30 minutes en secondes

# --- Nouvelle stratégie: range trading / scalping de profits ---
# Bracket de trading (le bot ne trade que dans cette zone)
PRIX_ACHAT_MIN = 0.0900
PRIX_ACHAT_MAX = 0.1800

# Achat: seuil minimum de USD disponible pour déclencher un achat
# (l'implémentation par défaut achète avec tout le solde USD disponible)
SOLDE_USD_MIN_POUR_ACHAT = 1000

# Prise de bénéfices: vendre uniquement le surplus dès qu'il dépasse ce seuil.
# Plus c'est petit, plus le bot "scalpe" souvent (mais attention aux frais).
SEUIL_BENEFICES_USD = 2.0

# Optionnel: n'essayer de prendre les bénéfices que si le prix a bougé d'au moins
# ce montant depuis la dernière vérification (évite de spammer des ventes).
DECLENCHEUR_MOUVEMENT_PRIX = 0.0002