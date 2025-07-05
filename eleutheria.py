#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de DCA optimisé pour Hedera (HBAR) sur Coinbase
Ce script:
- Surveille le prix de Hedera (HBAR) sur Coinbase
- Utilise une stratégie d'accumulation adaptative selon les zones de prix
- Prend des bénéfices par paliers, même à des prix plus bas
- Réinvestit une partie des bénéfices pour augmenter la position
- Intègre un système de stops dynamiques pour limiter les pertes
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
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eleutheria_trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("eleutheria")

# Import configuration
try:
    from config import *
except ImportError:
    # Fallback configuration if config.py doesn't exist
    API_KEY = "VOTRE_API_KEY"
    API_SECRET = "VOTRE_API_SECRET"
    API_PASSPHRASE = "VOTRE_API_PASSPHRASE"
    API_URL = "https://api.exchange.coinbase.com"
    HBAR_SYMBOL = "HBAR-USD"
    ZONES_ACHAT = [
        {"prix_max": 0.13, "prix_min": 0.12, "montant": 500, "pourcentage_capital": 0.10},
        {"prix_max": 0.12, "prix_min": 0.11, "montant": 750, "pourcentage_capital": 0.15},
        {"prix_max": 0.11, "prix_min": 0.10, "montant": 1000, "pourcentage_capital": 0.20},
        {"prix_max": 0.10, "prix_min": 0.09, "montant": 1500, "pourcentage_capital": 0.25},
        {"prix_max": 0.09, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
    ]
    ZONES_VENTE = [
        {"prix_min": 0.14, "pourcentage_benefices": 0.20},
        {"prix_min": 0.15, "pourcentage_benefices": 0.30},
        {"prix_min": 0.16, "pourcentage_benefices": 0.50},
        {"prix_min": 0.18, "pourcentage_benefices": 0.70},
        {"prix_min": 0.20, "pourcentage_benefices": 0.90}
    ]
    STOP_LOSS_POURCENTAGE = 0.15
    INTERVALLE_VERIFICATION_NORMAL = 1800
    INTERVALLE_VERIFICATION_OPPORTUNITE = 300

# Variables pour stocker les métriques
capital_initial = None
prix_moyen_achat = None
derniers_achats = []
dernieres_ventes = []
performance_historique = []
prix_plus_bas_24h = None
prix_plus_haut_24h = None

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
    try:
        response = requests.get(f"{API_URL}/products/{HBAR_SYMBOL}/ticker")
        if response.status_code != 200:
            logger.error(f"Erreur lors de la récupération du prix: {response.text}")
            return None
        
        data = response.json()
        return float(data["price"])
    except Exception as e:
        logger.error(f"Exception lors de la récupération du prix: {str(e)}")
        return None

def obtenir_donnees_marche_24h():
    """Obtient les données de marché des dernières 24h"""
    global prix_plus_bas_24h, prix_plus_haut_24h
    
    try:
        response = requests.get(f"{API_URL}/products/{HBAR_SYMBOL}/stats")
        if response.status_code != 200:
            logger.error(f"Erreur lors de la récupération des stats: {response.text}")
            return
        
        data = response.json()
        prix_plus_bas_24h = float(data["low"])
        prix_plus_haut_24h = float(data["high"])
        
        logger.info(f"Stats 24h - Plus bas: {prix_plus_bas_24h}$ | Plus haut: {prix_plus_haut_24h}$")
    except Exception as e:
        logger.error(f"Exception lors de la récupération des stats: {str(e)}")

def obtenir_solde_hbar():
    """Obtient le solde actuel de HBAR dans le compte"""
    try:
        headers = signer_requete("GET", "/accounts")
        response = requests.get(f"{API_URL}/accounts", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Erreur lors de la récupération des soldes: {response.text}")
            return 0
        
        accounts = response.json()
        for account in accounts:
            if account["currency"] == "HBAR":
                return float(account["available"])
        
        return 0
    except Exception as e:
        logger.error(f"Exception lors de la récupération du solde HBAR: {str(e)}")
        return 0

def obtenir_solde_usd():
    """Obtient le solde actuel d'USD dans le compte"""
    try:
        headers = signer_requete("GET", "/accounts")
        response = requests.get(f"{API_URL}/accounts", headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Erreur lors de la récupération des soldes: {response.text}")
            return 0
        
        accounts = response.json()
        for account in accounts:
            if account["currency"] == "USD":
                return float(account["available"])
        
        return 0
    except Exception as e:
        logger.error(f"Exception lors de la récupération du solde USD: {str(e)}")
        return 0

def calculer_capital_total():
    """Calcule le capital total présent sur le compte (USD + valeur des HBAR)"""
    solde_hbar = obtenir_solde_hbar()
    prix_actuel = obtenir_prix_hbar()
    solde_usd = obtenir_solde_usd()
    
    if not prix_actuel:
        logger.error("Impossible d'obtenir le prix actuel pour calculer le capital total")
        return None
    
    valeur_hbar = solde_hbar * prix_actuel
    capital_total = valeur_hbar + solde_usd
    
    logger.info(f"Capital total: {capital_total:.2f}$ (HBAR: {valeur_hbar:.2f}$ + USD: {solde_usd:.2f}$)")
    return capital_total

def calculer_prix_moyen_achat():
    """Calcule le prix moyen d'achat basé sur l'historique"""
    global prix_moyen_achat
    
    if not derniers_achats:
        # Si aucun historique, utiliser le prix actuel
        prix_moyen_achat = obtenir_prix_hbar()
        return prix_moyen_achat
    
    total_hbar = sum(achat["quantite"] for achat in derniers_achats)
    total_usd = sum(achat["montant"] for achat in derniers_achats)
    
    if total_hbar > 0:
        prix_moyen_achat = total_usd / total_hbar
        logger.info(f"Prix moyen d'achat: {prix_moyen_achat:.6f}$")
        return prix_moyen_achat
    
    return obtenir_prix_hbar()

def arrondir_montant(montant, decimales=6):
    """Arrondit un montant à un nombre spécifique de décimales"""
    return Decimal(str(montant)).quantize(Decimal('0.' + '0' * decimales), rounding=ROUND_DOWN)

def acheter_hbar(montant_usd):
    """Achète HBAR pour un montant spécifié en USD"""
    global derniers_achats
    
    prix_actuel = obtenir_prix_hbar()
    if not prix_actuel:
        return False
    
    # S'assurer que le montant est positif et ne dépasse pas le solde disponible
    solde_usd = obtenir_solde_usd()
    montant_usd = min(montant_usd, solde_usd)
    
    if montant_usd <= 0:
        logger.warning(f"Pas assez de USD disponible pour acheter (Solde: {solde_usd}$)")
        return False
    
    # Calcule la quantité de HBAR à acheter
    quantite_hbar = montant_usd / prix_actuel
    quantite_hbar = float(arrondir_montant(quantite_hbar))
    
    if quantite_hbar <= 0:
        logger.warning("Quantité à acheter trop petite")
        return False
    
    # Crée l'ordre d'achat
    ordre = {
        "side": "buy",
        "product_id": HBAR_SYMBOL,
        "type": "market",
        "size": str(quantite_hbar)
    }
    
    # Envoie l'ordre à Coinbase
    try:
        headers = signer_requete("POST", "/orders", json.dumps(ordre))
        response = requests.post(f"{API_URL}/orders", headers=headers, json=ordre)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Achat réussi de {quantite_hbar} HBAR à {prix_actuel}$ (Total: {montant_usd}$)")
            
            # Enregistre l'achat dans l'historique
            derniers_achats.append({
                "date": datetime.datetime.now().isoformat(),
                "prix": prix_actuel,
                "quantite": quantite_hbar,
                "montant": montant_usd
            })
            
            # Limite la taille de l'historique
            if len(derniers_achats) > 50:
                derniers_achats = derniers_achats[-50:]
            
            # Recalcule le prix moyen d'achat
            calculer_prix_moyen_achat()
            
            return True
        else:
            logger.error(f"Erreur lors de l'achat: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception lors de l'achat: {str(e)}")
        return False

def vendre_hbar(pourcentage_benefices):
    """Vend un pourcentage des bénéfices"""
    global dernieres_ventes, capital_initial
    
    solde_hbar = obtenir_solde_hbar()
    prix_actuel = obtenir_prix_hbar()
    
    if solde_hbar <= 0 or not prix_actuel:
        logger.warning("Aucun HBAR disponible à vendre ou prix non disponible")
        return False
    
    # Valeur actuelle du portefeuille
    valeur_totale = calculer_capital_total()
    
    if valeur_totale is None or capital_initial is None:
        logger.error("Impossible de calculer les valeurs nécessaires pour la vente")
        return False
    
    # Calcule les bénéfices
    benefices = valeur_totale - capital_initial
    
    if benefices <= 0:
        logger.info(f"Pas de bénéfices à prendre. Valeur: {valeur_totale:.2f}$ ≤ Capital initial: {capital_initial:.2f}$")
        return False
    
    # Calcule le montant à vendre en USD
    montant_a_vendre_usd = benefices * pourcentage_benefices
    
    # Calcule la quantité de HBAR à vendre
    quantite_a_vendre = montant_a_vendre_usd / prix_actuel
    quantite_a_vendre = min(quantite_a_vendre, solde_hbar)  # Ne pas vendre plus que disponible
    quantite_a_vendre = float(arrondir_montant(quantite_a_vendre))
    
    if quantite_a_vendre <= 0:
        logger.warning("Quantité à vendre trop petite")
        return False
    
    # Crée l'ordre de vente
    ordre = {
        "side": "sell",
        "product_id": HBAR_SYMBOL,
        "type": "market",
        "size": str(quantite_a_vendre)
    }
    
    # Envoie l'ordre à Coinbase
    try:
        headers = signer_requete("POST", "/orders", json.dumps(ordre))
        response = requests.post(f"{API_URL}/orders", headers=headers, json=ordre)
        
        if response.status_code in [200, 201]:
            montant_vendu = quantite_a_vendre * prix_actuel
            logger.info(f"✅ Vente réussie: {quantite_a_vendre} HBAR à {prix_actuel}$ (Total: {montant_vendu:.2f}$)")
            logger.info(f"Bénéfice pris: {pourcentage_benefices*100:.0f}% des bénéfices disponibles")
            
            # Enregistre la vente dans l'historique
            dernieres_ventes.append({
                "date": datetime.datetime.now().isoformat(),
                "prix": prix_actuel,
                "quantite": quantite_a_vendre,
                "montant": montant_vendu,
                "pourcentage_benefices": pourcentage_benefices
            })
            
            # Limite la taille de l'historique
            if len(dernieres_ventes) > 50:
                dernieres_ventes = dernieres_ventes[-50:]
            
            return True
        else:
            logger.error(f"Erreur lors de la vente: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception lors de la vente: {str(e)}")
        return False

def verifier_stop_loss():
    """Vérifie si le stop loss doit être déclenché"""
    global capital_initial
    
    if capital_initial is None:
        return False
    
    capital_actuel = calculer_capital_total()
    if capital_actuel is None:
        return False
    
    perte_pourcentage = (capital_initial - capital_actuel) / capital_initial
    
    if perte_pourcentage >= STOP_LOSS_POURCENTAGE:
        logger.warning(f"⚠️ STOP LOSS ATTEINT: Perte de {perte_pourcentage*100:.2f}% du capital")
        return True
    
    return False

def calculer_performance_actuelle():
    """Calcule la performance actuelle de la stratégie"""
    global capital_initial, performance_historique
    
    if capital_initial is None:
        return 0
    
    capital_actuel = calculer_capital_total()
    if capital_actuel is None:
        return 0
    
    performance = ((capital_actuel / capital_initial) - 1) * 100
    
    # Enregistre la performance dans l'historique
    performance_historique.append({
        "date": datetime.datetime.now().isoformat(),
        "capital": capital_actuel,
        "performance": performance
    })
    
    # Limite la taille de l'historique
    if len(performance_historique) > 100:
        performance_historique = performance_historique[-100:]
    
    return performance

def determiner_zone_achat(prix_actuel):
    """Détermine la zone d'achat appropriée en fonction du prix actuel"""
    for zone in ZONES_ACHAT:
        if zone["prix_min"] <= prix_actuel <= zone["prix_max"]:
            return zone
    return None

def determiner_zone_vente(prix_actuel):
    """Détermine la zone de vente appropriée en fonction du prix actuel"""
    # Trouver la zone de vente la plus élevée qui correspond au prix actuel
    zone_applicable = None
    for zone in ZONES_VENTE:
        if prix_actuel >= zone["prix_min"]:
            zone_applicable = zone
    return zone_applicable

def enregistrer_donnees():
    """Enregistre les données de trading dans un fichier JSON"""
    donnees = {
        "capital_initial": capital_initial,
        "prix_moyen_achat": prix_moyen_achat,
        "derniers_achats": derniers_achats,
        "dernieres_ventes": dernieres_ventes,
        "performance_historique": performance_historique,
        "date_dernier_enregistrement": datetime.datetime.now().isoformat()
    }
    
    try:
        with open("eleutheria_data.json", "w") as f:
            json.dump(donnees, f, indent=2)
        logger.info("Données de trading enregistrées")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des données: {str(e)}")

def charger_donnees():
    """Charge les données de trading depuis un fichier JSON"""
    global capital_initial, prix_moyen_achat, derniers_achats, dernieres_ventes, performance_historique
    
    try:
        if os.path.exists("eleutheria_data.json"):
            with open("eleutheria_data.json", "r") as f:
                donnees = json.load(f)
            
            capital_initial = donnees.get("capital_initial")
            prix_moyen_achat = donnees.get("prix_moyen_achat")
            derniers_achats = donnees.get("derniers_achats", [])
            dernieres_ventes = donnees.get("dernieres_ventes", [])
            performance_historique = donnees.get("performance_historique", [])
            
            logger.info("Données de trading chargées depuis le fichier")
            return True
        else:
            logger.info("Aucun fichier de données trouvé, démarrage avec des données vides")
            return False
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {str(e)}")
        return False

def afficher_rapport():
    """Affiche un rapport complet sur l'état actuel"""
    prix_actuel = obtenir_prix_hbar()
    if not prix_actuel:
        return
    
    solde_hbar = obtenir_solde_hbar()
    solde_usd = obtenir_solde_usd()
    valeur_hbar = solde_hbar * prix_actuel
    capital_actuel = valeur_hbar + solde_usd
    
    logger.info("\n" + "="*50)
    logger.info("📊 RAPPORT DE TRADING ELEUTHERIA")
    logger.info("="*50)
    logger.info(f"Date: {datetime.datetime.now()}")
    logger.info(f"Prix HBAR actuel: {prix_actuel:.6f}$")
    
    if prix_plus_bas_24h and prix_plus_haut_24h:
        logger.info(f"Variation 24h: {prix_plus_bas_24h:.6f}$ - {prix_plus_haut_24h:.6f}$")
    
    logger.info("-"*50)
    logger.info(f"Solde HBAR: {solde_hbar:.2f} (Valeur: {valeur_hbar:.2f}$)")
    logger.info(f"Solde USD: {solde_usd:.2f}$")
    logger.info(f"Capital total: {capital_actuel:.2f}$")
    
    if capital_initial:
        performance = ((capital_actuel / capital_initial) - 1) * 100
        logger.info(f"Capital initial: {capital_initial:.2f}$")
        logger.info(f"Performance: {performance:.2f}%")
    
    if prix_moyen_achat:
        logger.info(f"Prix moyen d'achat: {prix_moyen_achat:.6f}$")
        variation = ((prix_actuel / prix_moyen_achat) - 1) * 100
        logger.info(f"Variation par rapport au prix moyen: {variation:.2f}%")
    
    # Afficher les dernières transactions
    logger.info("-"*50)
    logger.info("DERNIÈRES TRANSACTIONS:")
    
    if derniers_achats:
        dernier_achat = derniers_achats[-1]
        logger.info(f"Dernier achat: {dernier_achat['quantite']:.2f} HBAR à {dernier_achat['prix']:.6f}$ " +
                  f"({dernier_achat['montant']:.2f}$) le {dernier_achat['date'].split('T')[0]}")
    
    if dernieres_ventes:
        derniere_vente = dernieres_ventes[-1]
        logger.info(f"Dernière vente: {derniere_vente['quantite']:.2f} HBAR à {derniere_vente['prix']:.6f}$ " +
                  f"({derniere_vente['montant']:.2f}$) le {derniere_vente['date'].split('T')[0]}")
    
    logger.info("="*50 + "\n")

def executer_strategie():
    """Exécute la stratégie de trading optimisée"""
    global capital_initial
    
    logger.info("🚀 Démarrage de la stratégie de trading Eleutheria pour HBAR...")
    
    # Charger les données précédentes si disponibles
    donnees_chargees = charger_donnees()
    
    # Si aucune donnée chargée ou pas de capital initial, calculer le capital initial
    if not donnees_chargees or capital_initial is None:
        capital_initial = calculer_capital_total()
        if not capital_initial:
            logger.error("Impossible de calculer le capital initial. Nouvelle tentative dans 1 minute...")
            time.sleep(60)
            capital_initial = calculer_capital_total()
            if not capital_initial:
                logger.error("Échec de la détection du capital initial. Arrêt du script.")
                return
    
    logger.info(f"Capital de référence: {capital_initial:.2f}$")
    
    # Obtenir les données de marché 24h
    obtenir_donnees_marche_24h()
    
    # Afficher le rapport initial
    afficher_rapport()
    
    # Boucle principale de trading
    while True:
        try:
            # Obtenir le prix actuel
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                logger.warning("Impossible d'obtenir le prix actuel, nouvelle tentative dans 5 minutes...")
                time.sleep(300)
                continue
            
            # Vérifier le stop loss
            if verifier_stop_loss():
                # En cas de stop loss, vendre une partie des HBAR pour sécuriser
                solde_hbar = obtenir_solde_hbar()
                if solde_hbar > 0:
                    quantite_a_vendre = solde_hbar * 0.5  # 50% du solde
                    ordre = {
                        "side": "sell",
                        "product_id": HBAR_SYMBOL,
                        "type": "market",
                        "size": str(float(arrondir_montant(quantite_a_vendre)))
                    }
                    
                    headers = signer_requete("POST", "/orders", json.dumps(ordre))
                    response = requests.post(f"{API_URL}/orders", headers=headers, json=ordre)
                    
                    if response.status_code in [200, 201]:
                        logger.warning(f"⚠️ STOP LOSS EXÉCUTÉ: Vendu {quantite_a_vendre} HBAR à {prix_actuel}$")
                        
                        # Recalculer le capital initial après le stop loss
                        time.sleep(5)  # Attendre que l'ordre se traite
                        capital_initial = calculer_capital_total()
                        logger.info(f"Nouveau capital de référence après stop loss: {capital_initial:.2f}$")
            
            # Calculer la performance actuelle
            performance = calculer_performance_actuelle()
            logger.info(f"Prix HBAR: {prix_actuel:.6f}$ | Performance: {performance:.2f}%")
            
            # Déterminer les actions à effectuer
            # 1. Vérifier s'il faut vendre (prioritaire)
            zone_vente = determiner_zone_vente(prix_actuel)
            if zone_vente:
                pourcentage_benefices = zone_vente["pourcentage_benefices"]
                logger.info(f"💰 Zone de vente détectée à {prix_actuel:.6f}$ (seuil: {zone_vente['prix_min']}$)")
                
                # Vérifier si on a des bénéfices à prendre
                capital_actuel = calculer_capital_total()
                if capital_actuel > capital_initial:
                    benefices = capital_actuel - capital_initial
                    logger.info(f"Bénéfices disponibles: {benefices:.2f}$")
                    
                    # Vendre le pourcentage approprié des bénéfices
                    vendre_hbar(pourcentage_benefices)
                else:
                    logger.info("Pas de bénéfices à prendre pour le moment")
            
            # 2. Vérifier s'il faut acheter
            else:
                zone_achat = determiner_zone_achat(prix_actuel)
                if zone_achat:
                    logger.info(f"💼 Zone d'achat détectée à {prix_actuel:.6f}$ (entre {zone_achat['prix_min']}$ et {zone_achat['prix_max']}$)")
                    
                    # Calcul du montant à acheter (fixe ou pourcentage du capital)
                    solde_usd = obtenir_solde_usd()
                    montant_fixe = zone_achat["montant"]
                    montant_pourcentage = capital_initial * zone_achat["pourcentage_capital"]
                    
                    # Prendre le plus petit des deux montants
                    montant_achat = min(montant_fixe, montant_pourcentage, solde_usd)
                    
                    # Vérifier si on a assez d'USD
                    if montant_achat > 0:
                        logger.info(f"Achat programmé pour {montant_achat:.2f}$")
                        acheter_hbar(montant_achat)
                    else:
                        logger.warning(f"Pas assez d'USD disponible pour acheter (Solde: {solde_usd:.2f}$)")
                else:
                    logger.info(f"📊 Prix actuel ({prix_actuel:.6f}$) hors des zones d'achat et de vente")
            
            # Enregistrer les données actuelles
            enregistrer_donnees()
            
            # Ajuster l'intervalle de vérification en fonction de la proximité des zones
            proximite_zone = False
            for zone in ZONES_ACHAT:
                if abs(prix_actuel - zone["prix_max"]) < 0.005 or abs(prix_actuel - zone["prix_min"]) < 0.005:
                    proximite_zone = True
                    break
            
            for zone in ZONES_VENTE:
                if abs(prix_actuel - zone["prix_min"]) < 0.005:
                    proximite_zone = True
                    break
            
            intervalle = INTERVALLE_VERIFICATION_OPPORTUNITE if proximite_zone else INTERVALLE_VERIFICATION_NORMAL
            
            # Afficher un rapport complet toutes les 24 heures
            if datetime.datetime.now().hour == 0 and datetime.datetime.now().minute < 30:
                afficher_rapport()
                # Obtenir les données de marché 24h
                obtenir_donnees_marche_24h()
            
            # Attendre avant la prochaine vérification
            logger.info(f"Prochaine vérification dans {intervalle // 60} minutes...")
            time.sleep(intervalle)
            
        except Exception as e:
            logger.error(f"Erreur dans la boucle principale: {str(e)}")
            logger.info("Reprise dans 5 minutes...")
            time.sleep(300)

def reinitialiser_parametres():
    """Réinitialise les paramètres du bot en fonction des conditions de marché"""
    prix_actuel = obtenir_prix_hbar()
    if not prix_actuel:
        return
    
    global ZONES_ACHAT, ZONES_VENTE
    
    # Adapter les zones d'achat et de vente en fonction du prix actuel
    if prix_actuel < 0.10:
        # Marché baissier - Adapter les zones
        ZONES_ACHAT = [
            {"prix_max": 0.10, "prix_min": 0.09, "montant": 500, "pourcentage_capital": 0.10},
            {"prix_max": 0.09, "prix_min": 0.08, "montant": 750, "pourcentage_capital": 0.15},
            {"prix_max": 0.08, "prix_min": 0.07, "montant": 1000, "pourcentage_capital": 0.20},
            {"prix_max": 0.07, "prix_min": 0.06, "montant": 1500, "pourcentage_capital": 0.25},
            {"prix_max": 0.06, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
        ]
        
        ZONES_VENTE = [
            {"prix_min": 0.11, "pourcentage_benefices": 0.20},
            {"prix_min": 0.12, "pourcentage_benefices": 0.30},
            {"prix_min": 0.13, "pourcentage_benefices": 0.50},
            {"prix_min": 0.14, "pourcentage_benefices": 0.70},
            {"prix_min": 0.15, "pourcentage_benefices": 0.90}
        ]
        
        logger.info("Paramètres adaptés pour un marché très baissier")
    
    elif prix_actuel < 0.13:
        # Conserver les paramètres par défaut
        pass
    
    elif prix_actuel < 0.17:
        # Marché légèrement haussier
        ZONES_ACHAT = [
            {"prix_max": 0.14, "prix_min": 0.13, "montant": 500, "pourcentage_capital": 0.10},
            {"prix_max": 0.13, "prix_min": 0.12, "montant": 750, "pourcentage_capital": 0.15},
            {"prix_max": 0.12, "prix_min": 0.11, "montant": 1000, "pourcentage_capital": 0.20},
            {"prix_max": 0.11, "prix_min": 0.10, "montant": 1500, "pourcentage_capital": 0.25},
            {"prix_max": 0.10, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
        ]
        
        ZONES_VENTE = [
            {"prix_min": 0.15, "pourcentage_benefices": 0.20},
            {"prix_min": 0.16, "pourcentage_benefices": 0.30},
            {"prix_min": 0.17, "pourcentage_benefices": 0.50},
            {"prix_min": 0.19, "pourcentage_benefices": 0.70},
            {"prix_min": 0.21, "pourcentage_benefices": 0.90}
        ]
        
        logger.info("Paramètres adaptés pour un marché légèrement haussier")
    
    elif prix_actuel >= 0.17:
        # Marché haussier
        ZONES_ACHAT = [
            {"prix_max": 0.17, "prix_min": 0.16, "montant": 500, "pourcentage_capital": 0.10},
            {"prix_max": 0.16, "prix_min": 0.15, "montant": 750, "pourcentage_capital": 0.15},
            {"prix_max": 0.15, "prix_min": 0.14, "montant": 1000, "pourcentage_capital": 0.20},
            {"prix_max": 0.14, "prix_min": 0.13, "montant": 1500, "pourcentage_capital": 0.25},
            {"prix_max": 0.13, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
        ]
        
        ZONES_VENTE = [
            {"prix_min": 0.18, "pourcentage_benefices": 0.20},
            {"prix_min": 0.19, "pourcentage_benefices": 0.30},
            {"prix_min": 0.20, "pourcentage_benefices": 0.50},
            {"prix_min": 0.22, "pourcentage_benefices": 0.70},
            {"prix_min": 0.24, "pourcentage_benefices": 0.90}
        ]
        
        logger.info("Paramètres adaptés pour un marché haussier")

def reprise_apres_erreur():
    """Fonction de reprise après une erreur majeure ou un redémarrage"""
    logger.info("🔄 Reprise du trading après erreur ou redémarrage...")
    
    # Charger les données
    charger_donnees()
    
    # Recalculer les métriques importantes
    calculer_capital_total()
    calculer_prix_moyen_achat()
    
    # Réinitialiser les paramètres en fonction des conditions de marché
    reinitialiser_parametres()
    
    # Afficher le rapport complet
    afficher_rapport()
    
    # Reprendre la boucle principale
    executer_strategie()

if __name__ == "__main__":
    # Vérifier que les clés API sont configurées
    if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
        logger.error("⛔ ERREUR: Veuillez configurer vos clés API Coinbase dans le script")
        exit(1)
    
    try:
        # Essayer de reprendre après une erreur éventuelle
        reprise_apres_erreur()
    except Exception as e:
        logger.critical(f"Erreur critique lors du démarrage: {str(e)}")
        
        # Dernière tentative de démarrage propre
        try:
            logger.info("Tentative de démarrage propre...")
            executer_strategie()
        except Exception as e:
            logger.critical(f"Échec du démarrage propre: {str(e)}")
            exit(1)
