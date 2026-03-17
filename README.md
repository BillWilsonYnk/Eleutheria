# 🤖 ELEUTHERIA
> Trading bot HBAR (Coinbase Exchange) en **temps réel** via **WebSocket**.

<div align="center">

![Version](https://img.shields.io/badge/Version-3.0-blue)
![Cryptocurrency](https://img.shields.io/badge/Crypto-HBAR-blueviolet)
![Platform](https://img.shields.io/badge/Platform-Coinbase_Exchange-orange)
![Mode](https://img.shields.io/badge/Mode-WebSocket%20Ticker-informational)

</div>

---

## ⚡ Ce qui a changé

- **Temps réel**: le bot écoute le flux `ticker` Coinbase via WebSocket (`wss://ws-feed.exchange.coinbase.com`).
- **Boucle async**: `asyncio` + `websockets` (plus de polling toutes les X minutes).
- **Mode LIVE**: `passer_ordre()` envoie des ordres réels à l’API Coinbase Brokerage (à utiliser avec prudence).
- **Nettoyage du repo**: les anciens fichiers Desktop/UI et scripts de lancement ont été retirés.
- **Logs**: journalisation dans `eleutheria_ws.log`.

---

## 🎯 Stratégie (résumé)

- **Entrée**: achat si le prix est dans la zone `[PRIX_ACHAT_MIN, PRIX_ACHAT_MAX]` et si `volume_24h` est suffisant.
- **Sortie**:
  - **Stop loss**: déclenchement si perte $\le -HARD\_STOP\_LOSS$.
  - **Trailing stop**: après un profit $\ge PROFIT\_MIN\_POUR\_SUIVI$, vente si le prix retombe de `DISTANCE_TRAILING_STOP` depuis le plus haut.
- **Coupe-circuit journalier**: si `pertes_du_jour >= PERTE_MAX_JOURNALIERE_EUR`, le bot arrête de trader.

---

## 📋 Prérequis

- **Python**: 3.8+ (recommandé 3.10+)
- **Compte Coinbase Exchange**: clés API avec droits de trading (uniquement si tu actives le mode réel)

---

## 🔧 Installation

```bash
git clone https://github.com/BillWilsonYnk/Eleutheria.git
cd Eleutheria
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Clés API (ne jamais commit)

Renseigne tes clés Coinbase via **variables d’environnement** :

- `COINBASE_API_KEY`
- `COINBASE_API_SECRET`

Un fichier d’exemple est fourni : `ENV.example` (à copier localement, sans commit).

Exemple (zsh/macOS) :

```bash
export COINBASE_API_KEY="..."
export COINBASE_API_SECRET="..."
```

Alternative: tu peux copier `ENV.example` vers un fichier local (ex: `.env`) puis l’exporter (le repo ignore déjà `.env`) :

```bash
cp ENV.example .env
set -a; source .env; set +a
```

### Paramètres de trading

Édite `config.py` (sans secrets) :

- **Trading**: `MONTANT_ACHAT`, `PRIX_ACHAT_MIN`, `PRIX_ACHAT_MAX`
- **Risk**: `HARD_STOP_LOSS`, `PERTE_MAX_JOURNALIERE_EUR`
- **Trailing**: `PROFIT_MIN_POUR_SUIVI`, `DISTANCE_TRAILING_STOP`

---

## 🚀 Utilisation

```bash
python eleutheria.py
```

- **Logs**: `eleutheria_ws.log`

---

## ✅ Trading réel (attention)

Ce bot est en **mode LIVE** dès que tu fournis `COINBASE_API_KEY` / `COINBASE_API_SECRET`.
Assure-toi de comprendre les paramètres de risque (`HARD_STOP_LOSS`, `PERTE_MAX_JOURNALIERE_EUR`) avant exécution.

---

## ⚠️ Avertissement

Le trading de crypto-monnaies comporte des risques significatifs. Ce bot est fourni à titre expérimental, sans garantie de résultat. N’investis que ce que tu peux te permettre de perdre.
