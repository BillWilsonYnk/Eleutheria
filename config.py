# -*- coding: utf-8 -*-

"""
Configuration file for Eleutheria Trading Bot
Replace the placeholder values with your actual Coinbase API credentials
"""

# Coinbase API Configuration
API_KEY = "VOTRE_API_KEY"  # Replace with your Coinbase API key
API_SECRET = "VOTRE_API_SECRET"  # Replace with your Coinbase API secret
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"  # Replace with your Coinbase API passphrase

# API URL
API_URL = "https://api.exchange.coinbase.com"

# Trading pair
HBAR_SYMBOL = "HBAR-USD"

# Trading Strategy Configuration
# Buy zones - adapted for current HBAR price around $0.13
ZONES_ACHAT = [
    {"prix_max": 0.13, "prix_min": 0.12, "montant": 500, "pourcentage_capital": 0.10},  # Zone 1
    {"prix_max": 0.12, "prix_min": 0.11, "montant": 750, "pourcentage_capital": 0.15},  # Zone 2
    {"prix_max": 0.11, "prix_min": 0.10, "montant": 1000, "pourcentage_capital": 0.20},  # Zone 3
    {"prix_max": 0.10, "prix_min": 0.09, "montant": 1500, "pourcentage_capital": 0.25},  # Zone 4
    {"prix_max": 0.09, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}   # Zone 5
]

# Sell zones - take profits at different levels
ZONES_VENTE = [
    {"prix_min": 0.14, "pourcentage_benefices": 0.20},  # Sell 20% of profits at $0.14
    {"prix_min": 0.15, "pourcentage_benefices": 0.30},  # Sell 30% of profits at $0.15
    {"prix_min": 0.16, "pourcentage_benefices": 0.50},  # Sell 50% of profits at $0.16
    {"prix_min": 0.18, "pourcentage_benefices": 0.70},  # Sell 70% of profits at $0.18
    {"prix_min": 0.20, "pourcentage_benefices": 0.90}   # Sell 90% of profits at $0.20
]

# Stop loss configuration
STOP_LOSS_POURCENTAGE = 0.15  # 15% maximum loss on total capital

# Trading intervals (in seconds)
INTERVALLE_VERIFICATION_NORMAL = 1800  # 30 minutes
INTERVALLE_VERIFICATION_OPPORTUNITE = 300  # 5 minutes

# UI Configuration
UI_THEME = "dark"  # Options: "dark", "light"
UI_REFRESH_RATE = 30  # UI refresh rate in seconds 