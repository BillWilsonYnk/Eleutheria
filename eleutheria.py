def calculer_capital_initial():
    """Calcule le capital initial présent sur le compte (USD + valeur des HBAR)"""
    solde_hbar = obtenir_solde_hbar()
    prix_actuel = obtenir_prix_hbar()
    solde_usd = obtenir_solde_usd()
    
    if not prix_actuel:
        print("Impossible d'obtenir le prix actuel pour calculer le capital initial")
        return None
    
    valeur_hbar = solde_hbar * prix_actuel
    capital_total = valeur_hbar + solde_usd
    
    print(f"Capital initial détecté: {capital_total}$ (HBAR: {valeur_hbar}$ + USD: {solde_usd}$)")
    return capital_total#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de DCA inverse pour Hedera (HBAR) sur Coinbase
Ce script:
- Surveille le prix de Hedera (HBAR) sur Coinbase
- Prend des bénéfices lorsque le prix monte au-dessus d'un seuil défini
- Rachète uniquement lorsque le prix est entre 0,17$ et 0,21$
- Utilise l'API Coinbase Pro (maintenant Coinbase Advanced)
"""

import time
import json
import hmac
import hashlib
import requests
import base64
import datetime
from urllib.parse import urlencode
import os
from decimal import Decimal, ROUND_DOWN

# Configuration
API_KEY = "VOTRE_API_KEY"  # À remplacer par votre clé API Coinbase
API_SECRET = "VOTRE_API_SECRET"  # À remplacer par votre secret API Coinbase
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"  # À remplacer par votre passphrase API Coinbase

API_URL = "https://api.exchange.coinbase.com"
HBAR_SYMBOL = "HBAR-USD"

# Paramètres de la stratégie
PRIX_ACHAT_MIN = 0.17  # Prix minimum pour acheter
PRIX_ACHAT_MAX = 0.21  # Prix maximum pour acheter
PRIX_VENTE_MIN = 0.23  # Prix minimum pour vendre (prendre des bénéfices)
MONTANT_ACHAT = 1000  # Montant en USD à acheter à chaque fois

# Variable pour stocker le capital initial détecté
capital_initial = None

# Intervalle de vérification du prix (en secondes)
INTERVALLE_VERIFICATION = 3600  # Vérifier chaque heure

def get_timestamp():
    """Retourne un timestamp au format ISO 8601"""
    return datetime.datetime.utcnow().isoformat() + "Z"

def signer_requete(method, endpoint, body=""):
    """Signe une requête pour l'API Coinbase"""
    timestamp = get_timestamp()
    message = timestamp + method + endpoint
    if body:
        message += body if isinstance(body, str) else json.dumps(body)
    signature = hmac.new(base64.b64decode(API_SECRET), message.encode('utf-8'), hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    
    return {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": signature_b64,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "CB-ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json"
    }

def obtenir_prix_hbar():
    """Obtient le prix actuel de HBAR sur Coinbase"""
    response = requests.get(f"{API_URL}/products/{HBAR_SYMBOL}/ticker")
    if response.status_code != 200:
        print(f"Erreur lors de la récupération du prix: {response.text}")
        return None
    
    data = response.json()
    return float(data["price"])

def obtenir_solde_hbar():
    """Obtient le solde actuel de HBAR dans le compte"""
    headers = signer_requete("GET", "/accounts")
    response = requests.get(f"{API_URL}/accounts", headers=headers)
    
    if response.status_code != 200:
        print(f"Erreur lors de la récupération des soldes: {response.text}")
        return 0
    
    accounts = response.json()
    for account in accounts:
        if account["currency"] == "HBAR":
            return float(account["available"])
    
    return 0

def obtenir_solde_usd():
    """Obtient le solde actuel d'USD dans le compte"""
    headers = signer_requete("GET", "/accounts")
    response = requests.get(f"{API_URL}/accounts", headers=headers)
    
    if response.status_code != 200:
        print(f"Erreur lors de la récupération des soldes: {response.text}")
        return 0
    
    accounts = response.json()
    for account in accounts:
        if account["currency"] == "USD":
            return float(account["available"])
    
    return 0

def arrondir_montant(montant, decimales=6):
    """Arrondit un montant à un nombre spécifique de décimales"""
    return Decimal(str(montant)).quantize(Decimal('0.' + '0' * decimales), rounding=ROUND_DOWN)

def acheter_hbar(montant_usd):
    """Achète HBAR pour un montant spécifié en USD"""
    prix_actuel = obtenir_prix_hbar()
    if not prix_actuel:
        return False
    
    # Calcule la quantité de HBAR à acheter
    quantite_hbar = montant_usd / prix_actuel
    quantite_hbar = float(arrondir_montant(quantite_hbar))
    
    # Crée l'ordre d'achat
    ordre = {
        "side": "buy",
        "product_id": HBAR_SYMBOL,
        "type": "market",
        "size": str(quantite_hbar)
    }
    
    # Envoie l'ordre à Coinbase
    headers = signer_requete("POST", "/orders", json.dumps(ordre))
    response = requests.post(f"{API_URL}/orders", headers=headers, json=ordre)
    
    if response.status_code in [200, 201]:
        print(f"Achat réussi de {quantite_hbar} HBAR à {prix_actuel}$ (Total: {montant_usd}$)")
        return True
    else:
        print(f"Erreur lors de l'achat: {response.text}")
        return False

def vendre_benefices():
    """Vend uniquement les bénéfices au-dessus du capital initial"""
    global capital_initial
    
    solde_hbar = obtenir_solde_hbar()
    prix_actuel = obtenir_prix_hbar()
    solde_usd = obtenir_solde_usd()
    
    if solde_hbar <= 0 or not prix_actuel:
        print("Aucun HBAR disponible à vendre ou prix non disponible")
        return False
    
    # Valeur actuelle du portefeuille en USD
    valeur_hbar = solde_hbar * prix_actuel
    valeur_totale = valeur_hbar + solde_usd
    
    # Si la valeur actuelle est inférieure au capital initial, pas de bénéfices à prendre
    if valeur_totale <= capital_initial:
        print(f"Pas de bénéfices à prendre. Valeur actuelle: {valeur_totale}$ < Capital initial: {capital_initial}$")
        return False
    
    # Calcule le montant des bénéfices en USD
    benefices_usd = valeur_totale - capital_initial
    
    # Calcule la quantité de HBAR à vendre pour obtenir ces bénéfices
    quantite_a_vendre = benefices_usd / prix_actuel
    quantite_a_vendre = float(arrondir_montant(quantite_a_vendre))
    
    if quantite_a_vendre <= 0:
        print("Quantité à vendre trop petite")
        return False
    
    # Crée l'ordre de vente
    ordre = {
        "side": "sell",
        "product_id": HBAR_SYMBOL,
        "type": "market",
        "size": str(quantite_a_vendre)
    }
    
    # Envoie l'ordre à Coinbase
    headers = signer_requete("POST", "/orders", json.dumps(ordre))
    response = requests.post(f"{API_URL}/orders", headers=headers, json=ordre)
    
    if response.status_code in [200, 201]:
        print(f"Vente des bénéfices réussie: {quantite_a_vendre} HBAR à environ {prix_actuel}$ (Total: {benefices_usd}$)")
        print(f"Capital préservé: {capital_initial}$")
        return True
    else:
        print(f"Erreur lors de la vente: {response.text}")
        return False

def executer_strategie():
    """Exécute la stratégie de DCA inverse"""
    global capital_initial
    
    print(f"Démarrage de la stratégie DCA inverse pour {HBAR_SYMBOL}...")
    print(f"Paramètres: Achat entre {PRIX_ACHAT_MIN}$ et {PRIX_ACHAT_MAX}$, vente des bénéfices quand prix ≥ {PRIX_VENTE_MIN}$")
    
    # Détecter le capital initial lors du démarrage
    capital_initial = calculer_capital_initial()
    if not capital_initial:
        print("Impossible de détecter le capital initial, nouvelle tentative dans 1 minute...")
        time.sleep(60)
        capital_initial = calculer_capital_initial()
        if not capital_initial:
            print("Échec de la détection du capital initial. Arrêt du script.")
            return
    
    print(f"Le script préservera le capital détecté: {capital_initial}$")
    
    while True:
        try:
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                print("Impossible d'obtenir le prix actuel, nouvelle tentative dans 5 minutes...")
                time.sleep(300)
                continue
            
            solde_hbar = obtenir_solde_hbar()
            solde_usd = obtenir_solde_usd()
            valeur_hbar = solde_hbar * prix_actuel
            valeur_totale = valeur_hbar + solde_usd
            benefices = valeur_totale - capital_initial if valeur_totale > capital_initial else 0
            
            print(f"\n--- {datetime.datetime.now()} ---")
            print(f"Prix HBAR: {prix_actuel}$")
            print(f"Solde HBAR: {solde_hbar} (Valeur: {valeur_hbar}$)")
            print(f"Solde USD: {solde_usd}$")
            print(f"Valeur totale: {valeur_totale}$")
            print(f"Capital à préserver: {capital_initial}$")
            print(f"Bénéfices actuels: {benefices}$")
            
            # Stratégie de vente (prendre uniquement les bénéfices)
            if prix_actuel >= PRIX_VENTE_MIN and benefices > 0:
                print(f"Prix favorable pour vendre les bénéfices ({prix_actuel}$ >= {PRIX_VENTE_MIN}$)")
                vendre_benefices()
            
            # Stratégie d'achat (acheter dans la fourchette de prix)
            elif PRIX_ACHAT_MIN <= prix_actuel <= PRIX_ACHAT_MAX and solde_usd >= MONTANT_ACHAT:
                print(f"Prix favorable pour acheter ({prix_actuel}$ entre {PRIX_ACHAT_MIN}$ et {PRIX_ACHAT_MAX}$)")
                print(f"Achat pour un montant de {MONTANT_ACHAT}$")
                acheter_hbar(MONTANT_ACHAT)
            
            else:
                print(f"Aucune action à effectuer. Le prix ({prix_actuel}$) n'est pas dans les zones d'achat ou de vente")
            
            # Attendre avant la prochaine vérification
            print(f"Prochaine vérification dans {INTERVALLE_VERIFICATION // 60} minutes...")
            time.sleep(INTERVALLE_VERIFICATION)
            
        except Exception as e:
            print(f"Erreur: {str(e)}")
            print("Reprise dans 5 minutes...")
            time.sleep(300)

if __name__ == "__main__":
    # Vérifier que les clés API sont configurées
    if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
        print("ERREUR: Veuillez configurer vos clés API Coinbase dans le script")
        exit(1)
    
    # Démarrer la stratégie
    executer_strategie()