# Eleutheria Desktop Trading App - Airbnb Style

A beautiful, modern desktop trading application inspired by Airbnb's clean and intuitive design. This app provides an elegant interface for automated HBAR trading on Coinbase with a focus on user experience and visual appeal.

## 🎨 Design Features

- **Airbnb-Inspired UI**: Clean white backgrounds, subtle shadows, and modern typography
- **Signature Red Accent**: Uses Airbnb's signature `#FF385C` red color for primary actions
- **Material Design Elements**: Rounded corners, hover effects, and smooth transitions
- **Responsive Layout**: Adapts to different window sizes with proper spacing
- **Professional Typography**: Uses Circular font family for a modern look
- **Color-Coded Status**: Green for positive performance, red for losses, gray for neutral

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- macOS, Windows, or Linux
- Coinbase Pro API credentials (optional for demo mode)

### Installation

1. **Clone or download the project**
   ```bash
   cd Eleutheria-1
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv eleutheria_env
   source eleutheria_env/bin/activate  # On Windows: eleutheria_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install tkinter (if needed)**
   - **macOS**: `brew install python-tk`
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **Windows**: Usually included with Python

5. **Run the Airbnb-style app**
   ```bash
   python3 run_airbnb.py
   ```

## 🎯 Features

### 📊 Real-Time Market Data
- Live HBAR price display with change indicators
- Color-coded performance metrics
- 24-hour price range tracking
- Portfolio value calculations

### 💼 Portfolio Management
- HBAR and USD balance tracking
- Total portfolio value display
- Average buy price calculation
- Performance percentage tracking

### 🎯 Trading Zones
- Visual display of buy and sell zones
- Real-time zone status indicators
- Zone-specific trading amounts
- Adaptive zone management

### 📈 Performance Tracking
- Real-time performance percentage
- Visual progress bar
- Historical performance data
- Profit/loss calculations

### 📝 Activity Logging
- Comprehensive trading activity log
- Timestamped entries
- Error tracking and reporting
- Log management tools

### ⚙️ Settings & Configuration
- API key management
- Trading parameter configuration
- Demo mode support
- Documentation links

## 🎨 UI Components

### Header Section
- **Logo**: Lightning bolt emoji with Airbnb red
- **Title**: "Eleutheria" in bold typography
- **Status Indicator**: Real-time trading status

### Navigation Bar
- **Start Trading**: Airbnb red button with hover effects
- **Stop Trading**: Dark button for stopping operations
- **Settings**: Teal button for configuration

### Price Display Card
- **Large Price**: Prominent HBAR price display
- **Change Indicator**: Color-coded percentage change
- **Real-time Updates**: Automatic price refresh

### Portfolio Stats
- **HBAR Balance**: Current HBAR holdings
- **USD Balance**: Available USD funds
- **Total Value**: Combined portfolio value

### Performance Section
- **Performance Metric**: Large percentage display
- **Average Buy Price**: Historical cost basis
- **Progress Bar**: Visual performance indicator

### Trading Zones
- **Buy Zones**: Price ranges for purchases
- **Sell Zones**: Profit-taking targets
- **Status Indicators**: Active/waiting states

### Activity Log
- **Transaction History**: Recent trades
- **System Messages**: Status updates
- **Error Reports**: Problem tracking

## 🔧 Configuration

### API Setup (Real Trading)

1. **Create config.py** in the project directory:
   ```python
   # Coinbase Pro API Configuration
   API_KEY = "your_api_key_here"
   API_SECRET = "your_api_secret_here"
   API_PASSPHRASE = "your_passphrase_here"
   API_URL = "https://api.exchange.coinbase.com"
   
   # Trading Parameters
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
   ```

2. **Get Coinbase Pro API credentials**:
   - Log into your Coinbase Pro account
   - Go to API settings
   - Create a new API key with trading permissions
   - Copy the key, secret, and passphrase

### Demo Mode

If no API keys are configured, the app runs in demo mode:
- Shows simulated data
- Displays the interface
- No real trading occurs
- Perfect for testing and learning

## 🎨 Design Philosophy

### Airbnb Design Principles Applied

1. **Clean & Minimal**: White backgrounds with subtle shadows
2. **Color Psychology**: Red for actions, green for success, gray for neutral
3. **Typography**: Modern, readable fonts with proper hierarchy
4. **Spacing**: Generous whitespace for better readability
5. **Feedback**: Clear visual feedback for all interactions
6. **Consistency**: Uniform design language throughout

### Color Palette

- **Primary Red**: `#FF385C` (Airbnb signature)
- **Secondary Teal**: `#00A699` (Success/positive)
- **Dark Gray**: `#222222` (Primary text)
- **Medium Gray**: `#717171` (Secondary text)
- **Light Gray**: `#F7F7F7` (Backgrounds)
- **White**: `#FFFFFF` (Main background)

## 🔒 Security Features

- **API Key Protection**: Secure storage of credentials
- **Demo Mode**: Safe testing without real funds
- **Error Handling**: Graceful failure management
- **Data Validation**: Input sanitization and verification

## 📱 Responsive Design

The app adapts to different screen sizes:
- **Minimum**: 1200x800 pixels
- **Recommended**: 1400x900 pixels or larger
- **Scaling**: Elements resize proportionally
- **Layout**: Flexible grid system

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named '_tkinter'"**
   - Install tkinter: `brew install python-tk` (macOS)
   - Or: `sudo apt-get install python3-tk` (Ubuntu)

2. **"Invalid color name"**
   - Update to latest version
   - Check for color value errors

3. **API connection errors**
   - Verify API credentials in config.py
   - Check internet connection
   - Ensure Coinbase Pro API is accessible

4. **Performance issues**
   - Close other applications
   - Reduce update frequency
   - Check system resources

### Getting Help

- Check the activity log for error messages
- Verify all dependencies are installed
- Ensure proper API configuration
- Review the original eleutheria.py for trading logic

## 🎯 Trading Strategy

The app implements the same DCA (Dollar Cost Averaging) strategy as the original script:

- **Adaptive Zones**: Buy zones adjust to market conditions
- **Profit Taking**: Sell zones for taking profits
- **Stop Loss**: Automatic loss protection
- **Reinvestment**: Partial profit reinvestment
- **Risk Management**: Capital preservation features

## 📈 Performance Monitoring

- Real-time performance tracking
- Historical data visualization
- Portfolio value monitoring
- Trade history logging
- Error tracking and reporting

## 🔄 Updates and Maintenance

- Regular price updates (30-second intervals)
- Automatic data saving
- Error recovery mechanisms
- Graceful shutdown handling

## 📄 License

This project is licensed under the same terms as the original Eleutheria trading bot.

---

**Enjoy trading with style! 🎨⚡** 