#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eleutheria Desktop Trading App - Airbnb Style
A beautiful, modern desktop application inspired by Airbnb's design
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import os
from datetime import datetime
import webbrowser
from PIL import Image, ImageTk, ImageDraw
import requests
import hmac
import hashlib
import base64
from decimal import Decimal, ROUND_DOWN
import math

# Import the trading logic from the original script
try:
    from eleutheria import (
        API_KEY, API_SECRET, API_PASSPHRASE, API_URL, HBAR_SYMBOL,
        ZONES_ACHAT, ZONES_VENTE, STOP_LOSS_POURCENTAGE,
        get_timestamp, signer_requete, obtenir_prix_hbar, obtenir_solde_hbar,
        obtenir_solde_usd, calculer_capital_total, acheter_hbar, vendre_hbar,
        enregistrer_donnees, charger_donnees
    )
except ImportError:
    # Fallback for demo mode
    API_KEY = "DEMO"
    API_SECRET = "DEMO"
    API_PASSPHRASE = "DEMO"
    API_URL = "https://api.exchange.coinbase.com"
    HBAR_SYMBOL = "HBAR-USD"
    ZONES_ACHAT = []
    ZONES_VENTE = []
    STOP_LOSS_POURCENTAGE = 0.15

class AirbnbButton(tk.Frame):
    """Airbnb-style button with hover effects"""
    def __init__(self, parent, text, command=None, bg="#FF385C", fg="white", 
                 hover_bg="#E31C5F", width=120, height=44, font_size=14, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), **kwargs)
        self.pack_propagate(False)
        
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.font_size = font_size
        self.state = "normal"
        
        # Create button
        self.button = tk.Label(self, text=text, bg=bg, fg=fg,
                              font=('Circular', font_size, 'bold'),
                              cursor="hand2")
        self.button.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind events
        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)
        self.button.bind("<Button-1>", self.on_click)
        self.button.bind("<ButtonRelease-1>", self.on_release)
    
    def on_enter(self, event):
        self.button.config(bg=self.hover_bg)
    
    def on_leave(self, event):
        self.button.config(bg=self.bg)
    
    def on_click(self, event):
        self.button.config(bg="#D70466")
    
    def on_release(self, event):
        self.button.config(bg=self.hover_bg)
        if self.command:
            self.command()

class AirbnbCard(tk.Frame):
    """Airbnb-style card with subtle shadow and rounded corners"""
    def __init__(self, parent, title="", subtitle="", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief="flat", bd=0, **kwargs)
        
        # Create card with shadow effect
        self.card_frame = tk.Frame(self, bg='#FFFFFF', relief="flat", bd=0)
        self.card_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Add subtle border for shadow effect
        self.border_frame = tk.Frame(self, bg='#DDDDDD', relief="flat", bd=0)
        self.border_frame.place(x=1, y=1, relwidth=1, relheight=1)
        self.border_frame.lower()
        
        # Title and subtitle
        if title:
            title_label = tk.Label(self.card_frame, text=title, 
                                  font=('Circular', 18, 'bold'),
                                  bg='#FFFFFF', fg='#222222')
            title_label.pack(anchor='w', padx=20, pady=(20, 5))
            
            if subtitle:
                subtitle_label = tk.Label(self.card_frame, text=subtitle, 
                                         font=('Circular', 14),
                                         bg='#FFFFFF', fg='#717171')
                subtitle_label.pack(anchor='w', padx=20, pady=(0, 20))

class PriceCard(tk.Frame):
    """Airbnb-style price display card"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief="flat", bd=0, **kwargs)
        
        # Price display
        self.price_label = tk.Label(self, text="$0.000000", 
                                   font=('Circular', 36, 'bold'),
                                   bg='#FFFFFF', fg='#222222')
        self.price_label.pack(pady=(20, 5))
        
        # Change indicator
        self.change_label = tk.Label(self, text="+0.00%", 
                                    font=('Circular', 16),
                                    bg='#FFFFFF', fg='#00A699')
        self.change_label.pack(pady=(0, 20))
        
        self.previous_price = None
    
    def update_price(self, price, change_percent=0):
        """Update price with Airbnb-style colors"""
        self.price_label.config(text=f"${price:.6f}")
        
        # Airbnb-style color coding
        if change_percent > 0:
            color = "#00A699"  # Airbnb green
        elif change_percent < 0:
            color = "#FF385C"  # Airbnb red
        else:
            color = "#717171"  # Airbnb gray
        
        self.change_label.config(text=f"{change_percent:+.2f}%", fg=color)

class StatCard(tk.Frame):
    """Airbnb-style statistics card"""
    def __init__(self, parent, title, value, color="#222222", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief="flat", bd=0, **kwargs)
        
        # Card content
        title_label = tk.Label(self, text=title, 
                              font=('Circular', 12),
                              bg='#FFFFFF', fg='#717171')
        title_label.pack(anchor='w', padx=15, pady=(15, 5))
        
        value_label = tk.Label(self, text=value, 
                              font=('Circular', 20, 'bold'),
                              bg='#FFFFFF', fg=color)
        value_label.pack(anchor='w', padx=15, pady=(0, 15))
        
        # Store reference
        self.value_label = value_label

class EleutheriaAirbnbApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eleutheria - Automated Trading")
        self.root.geometry("1400x900")
        self.root.configure(bg='#FFFFFF')  # Airbnb white background
        
        # Set window properties
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)
        
        # Trading state
        self.is_trading = False
        self.trading_thread = None
        self.capital_initial = None
        self.prix_moyen_achat = None
        self.derniers_achats = []
        self.dernieres_ventes = []
        self.performance_historique = []
        
        # Load data
        self.charger_donnees()
        
        # Create UI
        self.create_widgets()
        
        # Start price monitoring
        self.start_price_monitoring()
    
    def create_widgets(self):
        """Create the main UI widgets with Airbnb design"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#FFFFFF')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Navigation bar
        self.create_navigation(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#FFFFFF')
        content_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Top section - Price and controls
        self.create_top_section(content_frame)
        
        # Middle section - Stats and portfolio
        self.create_middle_section(content_frame)
        
        # Bottom section - Trading zones and logs
        self.create_bottom_section(content_frame)
    
    def create_header(self, parent):
        """Create Airbnb-style header"""
        header_frame = tk.Frame(parent, bg='#FFFFFF', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Logo and title
        logo_label = tk.Label(header_frame, 
                             text="⚡", 
                             font=('Circular', 32),
                             bg='#FFFFFF', 
                             fg='#FF385C')
        logo_label.pack(side='left', padx=40, pady=20)
        
        title_label = tk.Label(header_frame, 
                              text="Eleutheria", 
                              font=('Circular', 24, 'bold'),
                              bg='#FFFFFF', 
                              fg='#222222')
        title_label.pack(side='left', padx=(10, 0), pady=20)
        
        # Status indicator
        self.status_label = tk.Label(header_frame, 
                                    text="Ready to trade", 
                                    font=('Circular', 14),
                                    bg='#FFFFFF', 
                                    fg='#00A699')
        self.status_label.pack(side='right', padx=40, pady=20)
    
    def create_navigation(self, parent):
        """Create Airbnb-style navigation bar"""
        nav_frame = tk.Frame(parent, bg='#FFFFFF', height=60)
        nav_frame.pack(fill='x')
        nav_frame.pack_propagate(False)
        
        # Navigation buttons
        button_frame = tk.Frame(nav_frame, bg='#FFFFFF')
        button_frame.pack(expand=True)
        
        self.start_button = AirbnbButton(button_frame, 
                                        text="Start Trading", 
                                        command=self.start_trading,
                                        bg="#FF385C", 
                                        hover_bg="#E31C5F",
                                        width=140, 
                                        height=44,
                                        font_size=14)
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = AirbnbButton(button_frame, 
                                       text="Stop Trading", 
                                       command=self.stop_trading,
                                       bg="#222222", 
                                       hover_bg="#000000",
                                       width=140, 
                                       height=44,
                                       font_size=14)
        self.stop_button.pack(side='left', padx=10)
        
        self.settings_button = AirbnbButton(button_frame, 
                                           text="Settings", 
                                           command=self.open_settings,
                                           bg="#00A699", 
                                           hover_bg="#008489",
                                           width=120, 
                                           height=44,
                                           font_size=14)
        self.settings_button.pack(side='left', padx=10)
        
        # Initially disable stop button
        self.stop_button.button.config(state='disabled')
    
    def create_top_section(self, parent):
        """Create top section with price display and quick stats"""
        top_frame = tk.Frame(parent, bg='#FFFFFF')
        top_frame.pack(fill='x', pady=(0, 30))
        
        # Price card (left)
        price_card = AirbnbCard(top_frame, title="Current HBAR Price")
        price_card.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        self.price_display = PriceCard(price_card.card_frame)
        self.price_display.pack(fill='both', expand=True)
        
        # Quick stats (right)
        stats_frame = tk.Frame(top_frame, bg='#FFFFFF')
        stats_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Stats grid
        self.hbar_balance_card = StatCard(stats_frame, "HBAR Balance", "0.00", "#222222")
        self.hbar_balance_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.usd_balance_card = StatCard(stats_frame, "USD Balance", "$0.00", "#00A699")
        self.usd_balance_card.pack(side='left', fill='both', expand=True, padx=5)
        
        self.total_value_card = StatCard(stats_frame, "Total Value", "$0.00", "#FF385C")
        self.total_value_card.pack(side='left', fill='both', expand=True, padx=(10, 0))
    
    def create_middle_section(self, parent):
        """Create middle section with performance and portfolio"""
        middle_frame = tk.Frame(parent, bg='#FFFFFF')
        middle_frame.pack(fill='x', pady=(0, 30))
        
        # Performance card
        perf_card = AirbnbCard(middle_frame, title="Portfolio Performance", subtitle="Your trading results")
        perf_card.pack(fill='x')
        
        perf_content = tk.Frame(perf_card.card_frame, bg='#FFFFFF')
        perf_content.pack(fill='x', padx=20, pady=20)
        
        # Performance metrics
        self.performance_label = tk.Label(perf_content, 
                                         text="Performance: +0.00%", 
                                         font=('Circular', 24, 'bold'),
                                         bg='#FFFFFF', 
                                         fg='#00A699')
        self.performance_label.pack(anchor='w', pady=5)
        
        self.avg_price_label = tk.Label(perf_content, 
                                       text="Average Buy Price: $0.000000", 
                                       font=('Circular', 16),
                                       bg='#FFFFFF', 
                                       fg='#717171')
        self.avg_price_label.pack(anchor='w', pady=5)
        
        # Progress bar
        self.progress_frame = tk.Frame(perf_content, bg='#F7F7F7', height=8)
        self.progress_frame.pack(fill='x', pady=20)
        self.progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Frame(self.progress_frame, bg='#00A699', width=0)
        self.progress_bar.pack(side='left', fill='y')
    
    def create_bottom_section(self, parent):
        """Create bottom section with trading zones and activity"""
        bottom_frame = tk.Frame(parent, bg='#FFFFFF')
        bottom_frame.pack(fill='both', expand=True)
        
        # Left - Trading zones
        zones_card = AirbnbCard(bottom_frame, title="Trading Zones", subtitle="Buy and sell targets")
        zones_card.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        self.zones_text = scrolledtext.ScrolledText(zones_card.card_frame, 
                                                   bg='#FFFFFF', 
                                                   fg='#222222',
                                                   font=('Circular', 12),
                                                   relief='flat',
                                                   borderwidth=0)
        self.zones_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Right - Activity log
        log_card = AirbnbCard(bottom_frame, title="Trading Activity", subtitle="Recent transactions")
        log_card.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_card.card_frame, 
                                                 bg='#FFFFFF', 
                                                 fg='#222222',
                                                 font=('Circular', 12),
                                                 relief='flat',
                                                 borderwidth=0)
        self.log_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Clear log button
        clear_button = AirbnbButton(log_card.card_frame, 
                                   text="Clear Log", 
                                   command=self.clear_log,
                                   bg="#717171", 
                                   hover_bg="#565656",
                                   width=100, 
                                   height=36,
                                   font_size=12)
        clear_button.pack(anchor='w', padx=20, pady=(0, 20))
    
    def log_message(self, message):
        """Add a message to the log with Airbnb styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log size
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", "500.0")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete("1.0", tk.END)
    
    def update_price_display(self):
        """Update the price display with Airbnb colors"""
        try:
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                # Demo mode - use simulated price
                import random
                prix_actuel = 0.134500 + random.uniform(-0.002, 0.002)
            
            # Calculate change
            change_percent = 0
            if hasattr(self, 'previous_price') and self.previous_price:
                change_percent = ((prix_actuel - self.previous_price) / self.previous_price) * 100
            
            self.price_display.update_price(prix_actuel, change_percent)
            self.previous_price = prix_actuel
            
            # Update trading zones display
            self.update_zones_display()
            
        except Exception as e:
            self.log_message(f"Error updating price: {str(e)}")
    
    def update_portfolio_display(self):
        """Update the portfolio display with Airbnb styling"""
        try:
            solde_hbar = obtenir_solde_hbar()
            solde_usd = obtenir_solde_usd()
            prix_actuel = obtenir_prix_hbar()
            
            # Demo mode - use simulated data if API not available
            if solde_hbar == 0 and solde_usd == 0:
                solde_hbar = 15482.75
                solde_usd = 1245.67
                if not prix_actuel:
                    prix_actuel = 0.134500
            
            if prix_actuel:
                valeur_hbar = solde_hbar * prix_actuel
                total_value = valeur_hbar + solde_usd
                
                # Update stat cards
                self.hbar_balance_card.value_label.config(text=f"{solde_hbar:.2f}")
                self.usd_balance_card.value_label.config(text=f"${solde_usd:.2f}")
                self.total_value_card.value_label.config(text=f"${total_value:.2f}")
                
                # Update performance
                if not self.capital_initial:
                    self.capital_initial = 3000.0  # Demo initial capital
                
                performance = ((total_value / self.capital_initial) - 1) * 100
                if performance >= 0:
                    self.performance_label.config(text=f"Performance: +{performance:.2f}%", fg="#00A699")
                else:
                    self.performance_label.config(text=f"Performance: {performance:.2f}%", fg="#FF385C")
                
                # Update progress bar
                progress_width = max(0, min(300, (performance + 50) * 3))
                self.progress_bar.config(width=int(progress_width))
                
                # Update average price
                if not self.prix_moyen_achat:
                    self.prix_moyen_achat = 0.124800  # Demo average price
                self.avg_price_label.config(text=f"Average Buy Price: ${self.prix_moyen_achat:.6f}")
                
        except Exception as e:
            self.log_message(f"Error updating portfolio: {str(e)}")
    
    def update_zones_display(self):
        """Update the trading zones display with Airbnb styling"""
        try:
            self.zones_text.delete("1.0", tk.END)
            
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                prix_actuel = 0.134500  # Demo price
            
            # Display buy zones
            self.zones_text.insert(tk.END, "BUY ZONES:\n", "title")
            for i, zone in enumerate(ZONES_ACHAT, 1):
                in_zone = zone["prix_min"] <= prix_actuel <= zone["prix_max"]
                status = "🎯 ACTIVE" if in_zone else "⏸️ WAITING"
                
                zone_text = f"Zone {i}: ${zone['prix_min']:.3f} - ${zone['prix_max']:.3f} | ${zone['montant']} | {status}\n"
                self.zones_text.insert(tk.END, zone_text)
            
            self.zones_text.insert(tk.END, "\nSELL ZONES:\n", "title")
            for i, zone in enumerate(ZONES_VENTE, 1):
                in_zone = prix_actuel >= zone["prix_min"]
                status = "💰 ACTIVE" if in_zone else "⏸️ WAITING"
                
                zone_text = f"Zone {i}: ${zone['prix_min']:.3f}+ | {zone['pourcentage_benefices']*100:.0f}% | {status}\n"
                self.zones_text.insert(tk.END, zone_text)
                
        except Exception as e:
            self.log_message(f"Error updating zones: {str(e)}")
    
    def start_price_monitoring(self):
        """Start the price monitoring thread"""
        def monitor():
            while True:
                if not self.is_trading:
                    self.update_price_display()
                    self.update_portfolio_display()
                time.sleep(30)  # Update every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def start_trading(self):
        """Start the trading bot with Airbnb-style feedback"""
        if self.is_trading:
            return
        
        # Check API configuration
        if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
            messagebox.showwarning("Demo Mode", 
                               "Running in DEMO MODE - No real trading will occur.\n\nTo enable real trading, configure your Coinbase API keys in config.py")
            # Continue in demo mode
        
        self.is_trading = True
        self.status_label.config(text="Trading Active", fg='#00A699')
        self.start_button.button.config(state='disabled')
        self.stop_button.button.config(state='normal')
        
        self.log_message("🚀 Starting Eleutheria trading bot...")
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.trading_thread.start()
    
    def stop_trading(self):
        """Stop the trading bot with Airbnb-style feedback"""
        if not self.is_trading:
            return
        
        self.is_trading = False
        self.status_label.config(text="Trading Stopped", fg='#FF385C')
        self.start_button.button.config(state='normal')
        self.stop_button.button.config(state='disabled')
        
        self.log_message("⏹️ Trading bot stopped")
    
    def trading_loop(self):
        """Main trading loop with Airbnb-style error handling"""
        try:
            # Initialize capital if needed
            if not self.capital_initial:
                self.capital_initial = calculer_capital_total()
                if not self.capital_initial:
                    self.capital_initial = 3000.0  # Demo capital
            
            self.log_message(f"💰 Initial capital: ${self.capital_initial:.2f}")
            
            while self.is_trading:
                try:
                    # Get current price
                    prix_actuel = obtenir_prix_hbar()
                    if not prix_actuel:
                        prix_actuel = 0.134500 + (time.time() % 100) * 0.001  # Demo price
                    
                    # Check for trading opportunities
                    self.check_trading_opportunities(prix_actuel)
                    
                    # Update displays
                    self.update_price_display()
                    self.update_portfolio_display()
                    
                    # Save data
                    enregistrer_donnees()
                    
                    # Wait before next check
                    time.sleep(1800)  # 30 minutes
                    
                except Exception as e:
                    self.log_message(f"❌ Error in trading loop: {str(e)}")
                    time.sleep(300)
                    
        except Exception as e:
            self.log_message(f"❌ Critical error in trading: {str(e)}")
            self.stop_trading()
    
    def check_trading_opportunities(self, prix_actuel):
        """Check for trading opportunities with Airbnb-style logging"""
        # Check sell zones first
        zone_vente = self.determiner_zone_vente(prix_actuel)
        if zone_vente:
            self.log_message(f"💰 Sell zone detected at ${prix_actuel:.6f}")
            capital_actuel = calculer_capital_total()
            if capital_actuel and self.capital_initial and capital_actuel > self.capital_initial:
                benefices = capital_actuel - self.capital_initial
                self.log_message(f"📈 Profits available: ${benefices:.2f}")
                vendre_hbar(zone_vente["pourcentage_benefices"])
            return
        
        # Check buy zones
        zone_achat = self.determiner_zone_achat(prix_actuel)
        if zone_achat:
            self.log_message(f"💼 Buy zone detected at ${prix_actuel:.6f}")
            solde_usd = obtenir_solde_usd()
            montant_fixe = zone_achat["montant"]
            montant_pourcentage = self.capital_initial * zone_achat["pourcentage_capital"]
            montant_achat = min(montant_fixe, montant_pourcentage, solde_usd)
            
            if montant_achat > 0:
                self.log_message(f"📥 Buying for ${montant_achat:.2f}")
                acheter_hbar(montant_achat)
            else:
                self.log_message(f"⚠️ Insufficient USD for purchase (Balance: ${solde_usd:.2f})")
    
    def determiner_zone_achat(self, prix_actuel):
        """Determine the appropriate buy zone"""
        for zone in ZONES_ACHAT:
            if zone["prix_min"] <= prix_actuel <= zone["prix_max"]:
                return zone
        return None
    
    def determiner_zone_vente(self, prix_actuel):
        """Determine the appropriate sell zone"""
        zone_applicable = None
        for zone in ZONES_VENTE:
            if prix_actuel >= zone["prix_min"]:
                zone_applicable = zone
        return zone_applicable
    
    def charger_donnees(self):
        """Load trading data"""
        try:
            if os.path.exists("eleutheria_data.json"):
                with open("eleutheria_data.json", "r") as f:
                    donnees = json.load(f)
                
                self.capital_initial = donnees.get("capital_initial")
                self.prix_moyen_achat = donnees.get("prix_moyen_achat")
                self.derniers_achats = donnees.get("derniers_achats", [])
                self.dernieres_ventes = donnees.get("dernieres_ventes", [])
                self.performance_historique = donnees.get("performance_historique", [])
                
                self.log_message("📂 Trading data loaded")
        except Exception as e:
            self.log_message(f"⚠️ Error loading data: {str(e)}")
    
    def open_settings(self):
        """Open Airbnb-style settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Eleutheria Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg='#FFFFFF')
        
        # Settings content with Airbnb styling
        title = tk.Label(settings_window, 
                        text="Settings", 
                        font=('Circular', 24, 'bold'),
                        bg='#FFFFFF', 
                        fg='#222222')
        title.pack(pady=30)
        
        # API Status card
        api_card = AirbnbCard(settings_window, title="API Configuration", subtitle="Connect your Coinbase account")
        api_card.pack(fill='x', padx=20, pady=10)
        
        if API_KEY != "VOTRE_API_KEY":
            api_status = tk.Label(api_card.card_frame, 
                                 text="✅ API Keys Configured", 
                                 font=('Circular', 16),
                                 bg='#FFFFFF', 
                                 fg='#00A699')
        else:
            api_status = tk.Label(api_card.card_frame, 
                                 text="❌ API Keys Not Configured", 
                                 font=('Circular', 16),
                                 bg='#FFFFFF', 
                                 fg='#FF385C')
        api_status.pack(pady=20)
        
        # Help button
        help_button = AirbnbButton(settings_window, 
                                  text="View Documentation", 
                                  command=lambda: webbrowser.open("https://github.com/your-repo/eleutheria"),
                                  bg="#FF385C", 
                                  hover_bg="#E31C5F",
                                  width=180, 
                                  height=44,
                                  font_size=14)
        help_button.pack(pady=30)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EleutheriaAirbnbApp(root)
    
    # Handle window close
    def on_closing():
        if app.is_trading:
            if messagebox.askokcancel("Quit", "Trading is active. Do you want to stop trading and quit?"):
                app.stop_trading()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 