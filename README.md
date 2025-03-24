# 🚀 ELEUTHEIA 🚀

<div align="center">


### *The Autonomous Crypto Trading Bot That Never Sleeps*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Coinbase](https://img.shields.io/badge/Exchange-Coinbase-blue)](https://www.coinbase.com/)
[![Crypto](https://img.shields.io/badge/Crypto-HBAR-teal)](https://hedera.com/)

</div>

---

## 💎 WHAT IS THIS SORCERY? 💎

**HBAR Profit Harvester** is the ultimate "set it and forget it" trading bot for Hedera ($HBAR) that does one thing exceptionally well: **Makes you money while you sleep**.

This bot implements an **inverse DCA strategy** that:
- 📉 **BUYS** when prices drop into the sweet spot ($0.17-$0.21)
- 📈 **SELLS** only your profits when price surges ($0.23+)
- 🛡️ **PROTECTS** your principal investment at all costs
- 🔄 **REPEATS** this cycle to accumulate more HBAR over time

> *"Buy low, sell high, automate or die trying."*

---

## 🚀 THE EDGE YOU'VE BEEN LOOKING FOR 🚀

<table>
<tr>
<td width="50%">

### Without This Bot
- 😱 FOMO buying at market peaks
- 😰 Panic selling during dips
- 😴 Missing profit opportunities while sleeping
- 🤯 Emotional trading decisions
- ⏰ Constantly checking prices
- 📊 No systematic strategy
</td>
<td width="50%">

### With HBAR Profit Harvester
- 🤖 Automated buying at optimal prices
- 💰 Systematic profit taking
- 🔋 24/7 market monitoring
- 🧠 Emotion-free trading decisions
- ⛱️ Peace of mind & freedom
- 📈 Growing HBAR position over time
</td>
</tr>
</table>

---

## ⚡ INSTALLATION ⚡

```bash
# Clone this beast
git clone https://github.com/yourusername/hbar-profit-harvester.git

# Enter the money factory
cd hbar-profit-harvester

# Power it up
pip install -r requirements.txt

# Configure (see below)

# Release the Kraken
python hbar_profit_harvester.py
```

---

## 🔧 CONFIGURATION 🔧

1️⃣ Get your Coinbase API credentials (Settings → API → New API Key)
   * ✅ Enable trading permissions
   * ❌ Disable withdrawal permissions

2️⃣ Add your keys to the script:
```python
API_KEY = "your_coinbase_api_key"  # The key to the kingdom
API_SECRET = "your_coinbase_api_secret"  # Keep this SECRET
API_PASSPHRASE = "your_coinbase_api_passphrase"  # The magic words
```

3️⃣ Customize your strategy (or keep the proven defaults):
```python
BUY_PRICE_MIN = 0.17    # 📉 The bottom of your buy zone
BUY_PRICE_MAX = 0.21    # 📊 The top of your buy zone
SELL_PRICE_MIN = 0.23   # 📈 Your profit target
PURCHASE_AMOUNT = 1000  # 💸 How much to invest each time
CHECK_INTERVAL = 3600   # ⏱️ How often to check (in seconds)
```

---

## 🧠 HOW THE MAGIC HAPPENS 🧠

<div align="center">

```
         🔍 DETECT PORTFOLIO VALUE
                     │
                     ▼
            🔄 MONITOR HBAR PRICE
                     │
                     ▼
          ┌─────────────────────┐
          │  IS PRICE BETWEEN   │
          │  $0.17 AND $0.21?   │
          └─────────────────────┘
           /                    \
         YES                     NO
         /                         \
┌─────────────────┐                 ┌─────────────────┐
│  BUY $1000 HBAR │                 │ IS PRICE $0.23+ │
└─────────────────┘                 └─────────────────┘
         │                                  /     \
         │                               YES       NO
         │                               /          \
         │                ┌─────────────────────┐    │
         └───────────────►│ SELL ONLY PROFITS,  │    │
                          │ KEEP PRINCIPAL      │    │
                          └─────────────────────┘    │
                                    │                │
                                    └────────────────┘
                                          │
                                          ▼
                                    🔄 REPEAT
```

</div>

### 💡 Real-World Example:

* 💼 You start with: $3000 total portfolio
* 📈 HBAR price rises to $0.25, portfolio now worth $3800
* 🤖 Bot calculates: $3800 - $3000 = $800 profit
* 💰 Bot sells: Exactly $800 worth of HBAR
* 🔒 Your $3000 principal remains intact
* 📉 Price drops to $0.19 (buy zone)
* 🛒 Bot buys: $1000 worth of HBAR
* 🔁 Cycle repeats, growing your stack

---

## 🦾 ADVANCED FEATURES 🦾

* **Auto-Capital Detection**: Detects your starting portfolio value automatically
* **Partial Profit Taking**: Only harvests profits, leaving your base untouched
* **Dynamic Logging**: Detailed activity reports for monitoring
* **Error Handling**: Robust recovery from API failures
* **Flexible Timing**: Configurable check intervals

---

## ⚠️ DISCLAIMER ⚠️

*Trading cryptocurrency involves significant risk and potential for loss. This software is provided "as is" without warranty of any kind. The developers are not responsible for any losses incurred through the use of this bot. Use at your own risk and never invest more than you can afford to lose.*

---

## 📜 LICENSE 📜

MIT License - Do whatever you want with this code, just don't blame me if you lose money.


---

<div align="center">
  
*Built with ❤️ by crypto enthusiasts, for crypto enthusiasts*

**[⬆ back to top](#-hbar-profit-harvester-)**

</div>
