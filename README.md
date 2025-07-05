# 🤖 ELEUTHERIA
> *La liberté financière automatisée pour Hedera (HBAR)*

<div align="center">

![Version](https://img.shields.io/badge/Version-2.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Cryptocurrency](https://img.shields.io/badge/Crypto-HBAR-blueviolet)
![Platform](https://img.shields.io/badge/Platform-Coinbase-orange)

</div>

---

## 📊 Performances optimisées pour HBAR

Eleutheria a été entièrement repensé pour prospérer dans le marché actuel de Hedera. Que le prix monte ou descende, notre algorithme adaptatif trouve des opportunités de profit, même quand le marché semble stagner.

<div align="center">

| Stratégie précédente | Stratégie Eleutheria 2.0 |
|:-------------------:|:------------------------:|
| Achat entre 0,17$ et 0,21$ | Zones d'achat dynamiques adaptées au marché |
| Vente uniquement au-dessus de 0,23$ | Prise de bénéfices progressive dès 0,14$ |
| Paramètres fixes | Adaptation automatique aux conditions du marché |
| Pas de protection contre les pertes | Stop loss dynamique intégré |

</div>

---

## ⚡ Caractéristiques principales

### 🎯 Stratégie d'achat multi-niveaux intelligent
```
PRIX ACTUEL : 0,13$
⬇️ Zone 1 : 0,12$ - 0,13$ → Achat léger (10% du capital)
⬇️ Zone 2 : 0,11$ - 0,12$ → Achat modéré (15% du capital)
⬇️ Zone 3 : 0,10$ - 0,11$ → Achat moyen (20% du capital)
⬇️ Zone 4 : 0,09$ - 0,10$ → Achat important (25% du capital)
⬇️ Zone 5 : < 0,09$ → Achat massif (30% du capital)
```

### 💰 Prise de bénéfices échelonnée
```
PROFIT SÉCURISÉ À CHAQUE PALIER
↗️ 0,14$ → Vente de 20% des bénéfices 
↗️ 0,15$ → Vente de 30% des bénéfices
↗️ 0,16$ → Vente de 50% des bénéfices
↗️ 0,18$ → Vente de 70% des bénéfices
↗️ 0,20$ → Vente de 90% des bénéfices
```

### 🛡️ Protection sophistiquée du capital
- **Stop loss intelligent** : Limite les pertes à 15% maximum du capital
- **Préservation du capital initial** : Vente uniquement des bénéfices générés
- **Calcul prudent des investissements** : Basé sur la plus petite valeur entre montant fixe et pourcentage du capital

### 🧠 Intelligence artificielle de marché
- **Analyse 24h/24** : Surveille les plus hauts et plus bas pour détecter les tendances
- **Adaptation dynamique** : Ajuste automatiquement la stratégie selon les conditions
- **Intensification de la vigilance** : Augmente la fréquence des vérifications à l'approche des zones d'opportunité

### 🔄 Système auto-apprenant
- **Journalisation avancée** : Suivi détaillé de toutes les opérations et décisions
- **Historique de performance** : Enregistrement et analyse des résultats
- **Résilience exceptionnelle** : Récupération automatique après erreurs ou interruptions

---

## 📋 Prérequis

<div align="center">

| Composant | Version minimale |
|:--------:|:----------------:|
| 🐍 Python | 3.8+ |
| 🔑 API Coinbase | Permissions de trading |
| 💻 Système | 24/7 pour une performance optimale |

</div>

---

## 🔧 Installation

### 1️⃣ Récupérez la dernière version d'Eleutheria
```bash
git clone https://github.com/votre-compte/eleutheria.git
cd eleutheria
```

### 2️⃣ Installez les dépendances nécessaires
```bash
# Pour l'application desktop (recommandée)
pip install -r requirements.txt

# Ou pour l'interface en ligne de commande uniquement
pip install requests hmac hashlib
```

### 3️⃣ Configurez vos clés API Coinbase
```python
API_KEY = "VOTRE_API_KEY"
API_SECRET = "VOTRE_API_SECRET"
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"
```

---

## 🚀 Utilisation

### 🖥️ Application Desktop (Recommandée)
```bash
# Lanceur simple avec vérification des dépendances
python run_desktop.py

# Ou utilisez les lanceurs spécifiques à la plateforme
./run_desktop.sh          # macOS/Linux
run_desktop.bat           # Windows
```

### 💻 Interface en ligne de commande
```bash
python eleutheria.py
```

### Phases d'exécution automatique
1. **Initialisation** : Détection du capital et des conditions de marché
2. **Analyse** : Surveillance continue du prix de HBAR
3. **Exécution** : Achat et vente automatiques aux moments opportuns 
4. **Adaptation** : Ajustement des paramètres selon l'évolution du marché
5. **Reporting** : Génération de rapports quotidiens détaillés

### 🎯 Interface Desktop
L'application desktop offre :
- **Interface moderne** : Thème sombre professionnel
- **Données en temps réel** : Prix, portefeuille et performance
- **Contrôles interactifs** : Démarrage/arrêt du trading en un clic
- **Journalisation complète** : Logs détaillés des activités
- **Panneau de configuration** : Gestion facile des paramètres
- **Graphiques de prix** : Visualisation de l'historique des prix

---

## ⚙️ Personnalisation avancée

<details>
<summary>🔍 <b>Cliquez pour voir les options de personnalisation</b></summary>

### Zones d'achat
```python
ZONES_ACHAT = [
    {"prix_max": 0.13, "prix_min": 0.12, "montant": 500, "pourcentage_capital": 0.10},
    {"prix_max": 0.12, "prix_min": 0.11, "montant": 750, "pourcentage_capital": 0.15},
    {"prix_max": 0.11, "prix_min": 0.10, "montant": 1000, "pourcentage_capital": 0.20},
    {"prix_max": 0.10, "prix_min": 0.09, "montant": 1500, "pourcentage_capital": 0.25},
    {"prix_max": 0.09, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
]
```

### Zones de vente
```python
ZONES_VENTE = [
    {"prix_min": 0.14, "pourcentage_benefices": 0.20},
    {"prix_min": 0.15, "pourcentage_benefices": 0.30},
    {"prix_min": 0.16, "pourcentage_benefices": 0.50},
    {"prix_min": 0.18, "pourcentage_benefices": 0.70},
    {"prix_min": 0.20, "pourcentage_benefices": 0.90}
]
```

### Seuil de protection
```python
STOP_LOSS_POURCENTAGE = 0.15  # 15% de perte maximum
```

### Intervalles de vérification
```python
INTERVALLE_VERIFICATION_NORMAL = 1800  # 30 minutes
INTERVALLE_VERIFICATION_OPPORTUNITE = 300  # 5 minutes
```
</details>

---

## 📈 Tableau de bord et monitoring

### Fichiers générés automatiquement
- **📝 `eleutheria_trading.log`** : Journal détaillé de toutes les opérations
- **💾 `eleutheria_data.json`** : Données de trading et métriques de performance
- **📊 Rapport quotidien** : Généré automatiquement à minuit avec analyse complète

### Exemple de rapport journalier
```
======================================================
📊 RAPPORT DE TRADING ELEUTHERIA
======================================================
Date: 2025-04-07 00:00:15
Prix HBAR actuel: 0.134500$
Variation 24h: 0.128700$ - 0.136200$
------------------------------------------------------
Solde HBAR: 15482.75 (Valeur: 2082.43$)
Solde USD: 1245.67$
Capital total: 3328.10$
Capital initial: 3000.00$
Performance: 10.94%
Prix moyen d'achat: 0.124800$
Variation par rapport au prix moyen: 7.77%
------------------------------------------------------
DERNIÈRES TRANSACTIONS:
Dernier achat: 1500.00 HBAR à 0.125000$ (187.50$) le 2025-04-06
Dernière vente: 325.50 HBAR à 0.142000$ (46.22$) le 2025-04-06
======================================================
```

---

## ⚠️ Avertissement

<div align="center">
<table>
<tr>
<td>
<p align="center">
<b>CE BOT DE TRADING EST FOURNI À TITRE EXPÉRIMENTAL</b>
</p>

Le trading de crypto-monnaies comporte des risques significatifs. Vous pouvez perdre une partie ou la totalité de votre capital. Eleutheria Trading Bot est conçu pour optimiser les opportunités de profit, mais ne garantit aucun résultat. Utilisez-le à vos propres risques et n'investissez que ce que vous pouvez vous permettre de perdre.

</td>
</tr>
</table>
</div>

---

## 📜 Licence

<div align="center">

Ce projet est sous [licence MIT](LICENSE.md).

</div>

---

<p align="center">
<b>ELEUTHERIA © 2025</b><br>
<i>"L'autonomie financière à portée d'algorithme"</i>
</p>

<div align="center">
<p>
<b>Développé par Bill Wilson Yede Nka</b><br>
</p>
</div>
