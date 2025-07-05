# Eleutheria Desktop Trading App

A modern, user-friendly desktop application for automated HBAR (Hedera) trading on Coinbase. Built with Python and tkinter, featuring a sleek dark theme and real-time market data visualization.

## 🚀 Features

### Modern Desktop Interface
- **Dark Theme UI**: Sleek, professional dark interface
- **Real-time Updates**: Live price monitoring and portfolio tracking
- **Interactive Controls**: Start/stop trading with one click
- **Comprehensive Logging**: Detailed trading activity logs
- **Settings Panel**: Easy configuration management

### Trading Features
- **Automated DCA Strategy**: Dollar-cost averaging with adaptive zones
- **Smart Profit Taking**: Tiered profit-taking at different price levels
- **Dynamic Stop Loss**: Automatic loss protection
- **Portfolio Tracking**: Real-time balance and performance monitoring
- **Transaction History**: Complete buy/sell transaction log

### Market Data
- **Live Price Display**: Real-time HBAR price with change indicators
- **24h Statistics**: High/low prices and market movement
- **Trading Zones**: Visual representation of buy/sell zones
- **Performance Metrics**: Current profit/loss and average buy price

## 📋 Requirements

- Python 3.7 or higher
- Coinbase Pro API access
- Internet connection for real-time data

## 🛠️ Installation

### 1. Clone or Download
```bash
git clone <repository-url>
cd Eleutheria-1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Edit `config.py` and replace the placeholder values with your Coinbase API credentials:

```python
API_KEY = "your_actual_api_key"
API_SECRET = "your_actual_api_secret"
API_PASSPHRASE = "your_actual_passphrase"
```

### 4. Run the Application
```bash
python run_desktop.py
```

Or directly:
```bash
python eleutheria_desktop.py
```

## 🎯 Quick Start

1. **Launch the App**: Run `python run_desktop.py`
2. **Check Configuration**: Ensure API keys are properly configured
3. **Review Settings**: Check trading zones and parameters in the Settings panel
4. **Start Trading**: Click "🚀 START TRADING" to begin automated trading
5. **Monitor Activity**: Watch real-time updates in the interface

## 📊 Interface Overview

### Main Dashboard
- **Status Indicator**: Shows current trading state (Ready/Trading/Stopped)
- **Control Buttons**: Start, Stop, and Settings buttons
- **Live Price**: Current HBAR price with change percentage
- **Portfolio Summary**: HBAR balance, USD balance, and total value

### Market Data Panel
- **Price Display**: Large, prominent price with color-coded changes
- **24h Statistics**: High and low prices for the last 24 hours
- **Trading Zones**: Visual representation of configured buy/sell zones
- **Zone Status**: Active/inactive indicators for each zone

### Trading Information Panel
- **Balance Information**: Detailed breakdown of holdings
- **Performance Metrics**: Current profit/loss percentage
- **Average Buy Price**: Weighted average purchase price
- **Recent Transactions**: Last 5 buy/sell transactions

### Log Panel
- **Trading Log**: Real-time activity log with timestamps
- **Clear Log**: Button to clear the log display
- **Auto-scroll**: Automatically scrolls to show latest entries

## ⚙️ Configuration

### Trading Strategy Settings
The app uses a sophisticated DCA (Dollar-Cost Averaging) strategy with:

**Buy Zones**: 5 price zones with increasing investment amounts
- Zone 1: $0.12-$0.13 → $500 investment
- Zone 2: $0.11-$0.12 → $750 investment
- Zone 3: $0.10-$0.11 → $1000 investment
- Zone 4: $0.09-$0.10 → $1500 investment
- Zone 5: $0.00-$0.09 → $2000 investment

**Sell Zones**: 5 profit-taking levels
- $0.14 → Sell 20% of profits
- $0.15 → Sell 30% of profits
- $0.16 → Sell 50% of profits
- $0.18 → Sell 70% of profits
- $0.20 → Sell 90% of profits

### Risk Management
- **Stop Loss**: 15% maximum loss protection
- **Position Sizing**: Percentage-based and fixed amount limits
- **Profit Taking**: Gradual profit realization to maximize gains

## 🔧 Customization

### Modifying Trading Zones
Edit the `ZONES_ACHAT` and `ZONES_VENTE` arrays in `config.py`:

```python
ZONES_ACHAT = [
    {"prix_max": 0.13, "prix_min": 0.12, "montant": 500, "pourcentage_capital": 0.10},
    # Add or modify zones as needed
]

ZONES_VENTE = [
    {"prix_min": 0.14, "pourcentage_benefices": 0.20},
    # Add or modify zones as needed
]
```

### Adjusting Risk Parameters
```python
STOP_LOSS_POURCENTAGE = 0.15  # 15% stop loss
INTERVALLE_VERIFICATION_NORMAL = 1800  # 30 minutes
INTERVALLE_VERIFICATION_OPPORTUNITE = 300  # 5 minutes
```

## 📈 Trading Strategy

### DCA (Dollar-Cost Averaging) Approach
The app implements an intelligent DCA strategy that:
- Buys more when prices are lower
- Reduces average cost over time
- Takes profits at predetermined levels
- Manages risk with stop losses

### Adaptive Zones
- Buy zones are triggered when price falls within specified ranges
- Sell zones activate when price reaches profit targets
- Zones can be adjusted based on market conditions

### Risk Management
- Stop loss protection at 15% of total capital
- Position sizing limits to prevent overexposure
- Gradual profit taking to lock in gains

## 🚨 Safety Features

### API Security
- Secure API key storage in configuration file
- HMAC-SHA256 signature for all API requests
- Error handling for API failures

### Trading Safeguards
- Balance verification before trades
- Minimum trade amount validation
- Maximum position size limits
- Automatic error recovery

### Data Protection
- Local data storage in JSON format
- Automatic backup of trading history
- Secure logging without sensitive data exposure

## 📱 Usage Tips

### Getting Started
1. **Test with Small Amounts**: Start with small investments to test the strategy
2. **Monitor Performance**: Watch the performance metrics closely
3. **Adjust Settings**: Modify zones based on market conditions
4. **Keep Logs**: Review trading logs regularly for insights

### Best Practices
- **Regular Monitoring**: Check the app periodically during active trading
- **Market Awareness**: Be aware of major market events that might affect HBAR
- **Strategy Review**: Periodically review and adjust trading parameters
- **Backup Data**: Keep backups of your trading data

### Troubleshooting
- **API Errors**: Check your API keys and permissions
- **Connection Issues**: Ensure stable internet connection
- **Trading Errors**: Review logs for specific error messages
- **Performance Issues**: Restart the application if needed

## 🔄 Updates and Maintenance

### Data Persistence
- Trading data is automatically saved to `eleutheria_data.json`
- Configuration is stored in `config.py`
- Logs are maintained in the application interface

### Application Updates
- Check for updates to the trading strategy
- Review new features and improvements
- Update dependencies as needed

## ⚠️ Disclaimer

This application is for educational and personal use only. Cryptocurrency trading involves significant risk, and you should:

- Never invest more than you can afford to lose
- Understand the risks involved in cryptocurrency trading
- Consider consulting with a financial advisor
- Test the strategy thoroughly before using real funds

The developers are not responsible for any financial losses incurred through the use of this application.

## 📞 Support

For issues, questions, or suggestions:
- Check the logs for error messages
- Review the configuration settings
- Ensure all dependencies are properly installed
- Verify API credentials are correct

## 🎉 Enjoy Trading!

The Eleutheria Desktop Trading App provides a powerful, user-friendly interface for automated HBAR trading. With its modern design and sophisticated trading strategy, you can confidently manage your cryptocurrency investments while maintaining full control over your trading parameters.

Happy trading! 🚀 