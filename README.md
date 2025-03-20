# 🚀 HBAR PROFIT HARVESTER 🚀
*Automated Inverse DCA Trading Bot for Hedera*

![Hedera](https://raw.githubusercontent.com/hashgraph/hedera-improvement-proposal/main/assets/hip/logos/HIP_Logo_Color_Dark.png)

## 💰 Never Miss a Profit Opportunity Again 💰

The HBAR Profit Harvester is an intelligent trading bot that automatically buys Hedera during price dips and harvests profits during price increases - all while protecting your initial investment.

---

## ✨ FEATURES

- **🔍 Smart Capital Detection** - Automatically identifies your total portfolio value
- **💸 Dip Buying** - Automatically purchases $1000 HBAR when price hits the sweet spot ($0.17-$0.21)
- **📈 Profit Harvesting** - Intelligently sells ONLY your profits when price rises above $0.23
- **🛡️ Capital Shield** - Preserves your initial investment at all costs
- **⏱️ 24/7 Market Monitoring** - Works while you sleep

---

## 🔧 SETUP

### Requirements
- Coinbase account with API access
- Python 3.6+
- Basic dependencies (requests, time, json, etc.)

### Quick Start
```bash
# 1. Clone or download
git clone https://github.com/yourusername/hbar-profit-harvester.git

# 2. Install requirements
pip install requests

# 3. Configure your API keys
# Edit the script and add your keys:
# API_KEY = "your_key_here"
# API_SECRET = "your_secret_here"
# API_PASSPHRASE = "your_passphrase_here"

# 4. Launch the bot
python hbar_profit_harvester.py
```

---

## 🧠 HOW IT WORKS

### The Profit Cycle
```
┌────────────────────┐
│                    │
│ DETECT PORTFOLIO   │◄────────────────────┐
│ VALUE              │                     │
│                    │                     │
└─────────┬──────────┘                     │
          │                                │
          ▼                                │
┌────────────────────┐                     │
│                    │                     │
│ MONITOR PRICE      │                     │
│                    │                     │
└─────────┬──────────┘                     │
          │                                │
          ▼                                │
┌────────────────────┐     ┌──────────────┴───┐
│  PRICE BETWEEN     │     │                   │
│  $0.17 and $0.21?  │ No  │ PRICE ABOVE       │
├────────────────────┤────►│ $0.23?            │
│        Yes         │     │                   │
└─────────┬──────────┘     └──────────┬────────┘
          │                           │
          ▼                           │
┌────────────────────┐                │ Yes
│                    │                │
│ BUY $1000 HBAR     │                │
│                    │                ▼
└─────────┬──────────┘     ┌────────────────────┐
          │                │                    │
          └───────────────►│ SELL ONLY PROFITS  │
                           │                    │
                           └────────────────────┘
```

### Real-World Example

Starting with $3000 investment:

1. Bot detects your $3000 portfolio as your protected capital
2. HBAR price rises to $0.25, your portfolio now worth $3800
3. Bot automatically sells $800 worth of HBAR (the profit)
4. Your original $3000 remains intact
5. Price drops to $0.19, bot buys $1000 more HBAR
6. Cycle repeats, gradually increasing your HBAR position

---

## 🛠️ CONFIGURATION

Easily customize your strategy by modifying these parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| BUY_PRICE_MIN | $0.17 | Minimum price to start buying |
| BUY_PRICE_MAX | $0.21 | Maximum price for buying |
| SELL_PRICE_MIN | $0.23 | Minimum price to start selling profits |
| PURCHASE_AMOUNT | $1000 | Amount to buy with each transaction |
| CHECK_INTERVAL | 3600s | How often to check prices (in seconds) |

---

## ⚠️ IMPORTANT NOTES

- **Run on a reliable server** - A cloud VPS works best for 24/7 operation
- **Secure your API keys** - Only grant trading permissions, never withdrawal
- **Monitor regularly** - Check on your bot's performance weekly
- **Start small** - Test with smaller amounts until you're comfortable

---

## 📊 RESULTS

Users report:
- Less emotional trading decisions
- Consistent profit taking during volatility
- Growing HBAR positions over time
- Peace of mind from capital protection

---

## 📜 DISCLAIMER

*This tool is provided for educational purposes only. Cryptocurrency trading involves significant risk of loss. Past performance is not indicative of future results. Use at your own risk.*

---

## 🤝 CONTRIBUTE

Found a bug or want to improve the bot? PRs welcome!

## 📄 LICENSE

[MIT License](LICENSE) - Do whatever you want with this, just don't blame me if you lose money.

---

*"Buy the dip, sell the rip, automate the trip."* 🚀
