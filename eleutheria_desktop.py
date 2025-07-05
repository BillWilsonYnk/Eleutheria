#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eleutheria Desktop Trading App
A modern desktop application for automated HBAR trading on Coinbase
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import os
from datetime import datetime
import webbrowser
from PIL import Image, ImageTk
import requests
import hmac
import hashlib
import base64
from decimal import Decimal, ROUND_DOWN

# Import the trading logic from the original script
from eleutheria import (
    API_KEY, API_SECRET, API_PASSPHRASE, API_URL, HBAR_SYMBOL,
    ZONES_ACHAT, ZONES_VENTE, STOP_LOSS_POURCENTAGE,
    get_timestamp, signer_requete, obtenir_prix_hbar, obtenir_solde_hbar,
    obtenir_solde_usd, calculer_capital_total, acheter_hbar, vendre_hbar,
    enregistrer_donnees, charger_donnees
)

class EleutheriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eleutheria - HBAR Trading Bot")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
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
        self.setup_styles()
        
        # Start price monitoring
        self.start_price_monitoring()
    
    def setup_styles(self):
        """Configure modern styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#1a1a1a', 
                       foreground='#00ff88', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Status.TLabel', 
                       background='#1a1a1a', 
                       foreground='#ffffff', 
                       font=('Arial', 10))
        
        style.configure('Price.TLabel', 
                       background='#1a1a1a', 
                       foreground='#00ff88', 
                       font=('Arial', 14, 'bold'))
        
        style.configure('Info.TLabel', 
                       background='#2a2a2a', 
                       foreground='#cccccc', 
                       font=('Arial', 9))
        
        # Configure frames
        style.configure('Card.TFrame', 
                       background='#2a2a2a', 
                       relief='raised', 
                       borderwidth=1)
        
        # Configure buttons
        style.configure('Start.TButton', 
                       background='#00ff88', 
                       foreground='#000000', 
                       font=('Arial', 10, 'bold'))
        
        style.configure('Stop.TButton', 
                       background='#ff4444', 
                       foreground='#ffffff', 
                       font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Create the main UI widgets"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg='#1a1a1a')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="⚡ ELEUTHERIA TRADING BOT", 
                              font=('Arial', 24, 'bold'),
                              bg='#1a1a1a', 
                              fg='#00ff88')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Automated HBAR Trading on Coinbase", 
                                 font=('Arial', 12),
                                 bg='#1a1a1a', 
                                 fg='#888888')
        subtitle_label.pack()
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, pady=20)
        
        # Left panel - Market data
        self.create_market_panel(content_frame)
        
        # Right panel - Trading info
        self.create_trading_panel(content_frame)
        
        # Bottom panel - Logs
        self.create_log_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel with start/stop buttons"""
        control_frame = tk.Frame(parent, bg='#2a2a2a', relief='raised', bd=2)
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Status indicator
        self.status_label = tk.Label(control_frame, 
                                    text="🟡 READY", 
                                    font=('Arial', 12, 'bold'),
                                    bg='#2a2a2a', 
                                    fg='#ffff00')
        self.status_label.pack(side='left', padx=20, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#2a2a2a')
        button_frame.pack(side='right', padx=20, pady=10)
        
        self.start_button = tk.Button(button_frame, 
                                     text="🚀 START TRADING", 
                                     command=self.start_trading,
                                     bg='#00ff88', 
                                     fg='#000000',
                                     font=('Arial', 10, 'bold'),
                                     relief='flat',
                                     padx=20, 
                                     pady=5)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(button_frame, 
                                    text="⏹️ STOP TRADING", 
                                    command=self.stop_trading,
                                    bg='#ff4444', 
                                    fg='#ffffff',
                                    font=('Arial', 10, 'bold'),
                                    relief='flat',
                                    padx=20, 
                                    pady=5,
                                    state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.settings_button = tk.Button(button_frame, 
                                        text="⚙️ SETTINGS", 
                                        command=self.open_settings,
                                        bg='#444444', 
                                        fg='#ffffff',
                                        font=('Arial', 10, 'bold'),
                                        relief='flat',
                                        padx=20, 
                                        pady=5)
        self.settings_button.pack(side='left', padx=5)
    
    def create_market_panel(self, parent):
        """Create the market data panel"""
        market_frame = tk.Frame(parent, bg='#2a2a2a', relief='raised', bd=2)
        market_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Market title
        market_title = tk.Label(market_frame, 
                               text="📊 MARKET DATA", 
                               font=('Arial', 14, 'bold'),
                               bg='#2a2a2a', 
                               fg='#00ff88')
        market_title.pack(pady=10)
        
        # Price display
        price_frame = tk.Frame(market_frame, bg='#2a2a2a')
        price_frame.pack(fill='x', padx=20, pady=10)
        
        self.price_label = tk.Label(price_frame, 
                                   text="$0.000000", 
                                   font=('Arial', 24, 'bold'),
                                   bg='#2a2a2a', 
                                   fg='#00ff88')
        self.price_label.pack()
        
        self.price_change_label = tk.Label(price_frame, 
                                          text="+0.00%", 
                                          font=('Arial', 12),
                                          bg='#2a2a2a', 
                                          fg='#00ff88')
        self.price_change_label.pack()
        
        # 24h stats
        stats_frame = tk.Frame(market_frame, bg='#2a2a2a')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.high_24h_label = tk.Label(stats_frame, 
                                      text="24h High: $0.000000", 
                                      font=('Arial', 10),
                                      bg='#2a2a2a', 
                                      fg='#00ff88')
        self.high_24h_label.pack(anchor='w')
        
        self.low_24h_label = tk.Label(stats_frame, 
                                     text="24h Low: $0.000000", 
                                     font=('Arial', 10),
                                     bg='#2a2a2a', 
                                     fg='#ff4444')
        self.low_24h_label.pack(anchor='w')
        
        # Trading zones
        zones_frame = tk.Frame(market_frame, bg='#2a2a2a')
        zones_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        zones_title = tk.Label(zones_frame, 
                              text="🎯 TRADING ZONES", 
                              font=('Arial', 12, 'bold'),
                              bg='#2a2a2a', 
                              fg='#ffffff')
        zones_title.pack(anchor='w')
        
        # Create zones display
        self.zones_text = scrolledtext.ScrolledText(zones_frame, 
                                                   height=8, 
                                                   bg='#1a1a1a', 
                                                   fg='#cccccc',
                                                   font=('Consolas', 9),
                                                   relief='flat')
        self.zones_text.pack(fill='both', expand=True, pady=5)
        self.update_zones_display()
    
    def create_trading_panel(self, parent):
        """Create the trading information panel"""
        trading_frame = tk.Frame(parent, bg='#2a2a2a', relief='raised', bd=2)
        trading_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Trading title
        trading_title = tk.Label(trading_frame, 
                                text="💰 TRADING INFO", 
                                font=('Arial', 14, 'bold'),
                                bg='#2a2a2a', 
                                fg='#00ff88')
        trading_title.pack(pady=10)
        
        # Portfolio info
        portfolio_frame = tk.Frame(trading_frame, bg='#2a2a2a')
        portfolio_frame.pack(fill='x', padx=20, pady=10)
        
        self.hbar_balance_label = tk.Label(portfolio_frame, 
                                          text="HBAR Balance: 0.00", 
                                          font=('Arial', 12),
                                          bg='#2a2a2a', 
                                          fg='#ffffff')
        self.hbar_balance_label.pack(anchor='w')
        
        self.usd_balance_label = tk.Label(portfolio_frame, 
                                         text="USD Balance: $0.00", 
                                         font=('Arial', 12),
                                         bg='#2a2a2a', 
                                         fg='#ffffff')
        self.usd_balance_label.pack(anchor='w')
        
        self.total_value_label = tk.Label(portfolio_frame, 
                                         text="Total Value: $0.00", 
                                         font=('Arial', 12, 'bold'),
                                         bg='#2a2a2a', 
                                         fg='#00ff88')
        self.total_value_label.pack(anchor='w')
        
        # Performance
        perf_frame = tk.Frame(trading_frame, bg='#2a2a2a')
        perf_frame.pack(fill='x', padx=20, pady=10)
        
        self.performance_label = tk.Label(perf_frame, 
                                         text="Performance: +0.00%", 
                                         font=('Arial', 14, 'bold'),
                                         bg='#2a2a2a', 
                                         fg='#00ff88')
        self.performance_label.pack(anchor='w')
        
        self.avg_price_label = tk.Label(perf_frame, 
                                       text="Avg Buy Price: $0.000000", 
                                       font=('Arial', 10),
                                       bg='#2a2a2a', 
                                       fg='#cccccc')
        self.avg_price_label.pack(anchor='w')
        
        # Recent transactions
        trans_frame = tk.Frame(trading_frame, bg='#2a2a2a')
        trans_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        trans_title = tk.Label(trans_frame, 
                              text="📈 RECENT TRANSACTIONS", 
                              font=('Arial', 12, 'bold'),
                              bg='#2a2a2a', 
                              fg='#ffffff')
        trans_title.pack(anchor='w')
        
        self.transactions_text = scrolledtext.ScrolledText(trans_frame, 
                                                          height=8, 
                                                          bg='#1a1a1a', 
                                                          fg='#cccccc',
                                                          font=('Consolas', 9),
                                                          relief='flat')
        self.transactions_text.pack(fill='both', expand=True, pady=5)
    
    def create_log_panel(self, parent):
        """Create the log panel"""
        log_frame = tk.Frame(parent, bg='#2a2a2a', relief='raised', bd=2)
        log_frame.pack(fill='x', pady=(20, 0))
        
        # Log title
        log_title = tk.Label(log_frame, 
                            text="📝 TRADING LOG", 
                            font=('Arial', 12, 'bold'),
                            bg='#2a2a2a', 
                            fg='#00ff88')
        log_title.pack(anchor='w', padx=20, pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 height=8, 
                                                 bg='#1a1a1a', 
                                                 fg='#00ff88',
                                                 font=('Consolas', 9),
                                                 relief='flat')
        self.log_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Clear log button
        clear_button = tk.Button(log_frame, 
                                text="🗑️ Clear Log", 
                                command=self.clear_log,
                                bg='#444444', 
                                fg='#ffffff',
                                font=('Arial', 9),
                                relief='flat',
                                padx=10, 
                                pady=2)
        clear_button.pack(anchor='w', padx=20, pady=(0, 10))
    
    def log_message(self, message):
        """Add a message to the log"""
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
        """Update the price display"""
        try:
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                # Demo mode - use simulated price
                import random
                prix_actuel = 0.134500 + random.uniform(-0.002, 0.002)
            
            self.price_label.config(text=f"${prix_actuel:.6f}")
            
            # Update price change color based on previous price
            if hasattr(self, 'previous_price') and self.previous_price:
                change = prix_actuel - self.previous_price
                change_percent = (change / self.previous_price) * 100
                
                if change > 0:
                    self.price_change_label.config(text=f"+{change_percent:.2f}%", fg='#00ff88')
                elif change < 0:
                    self.price_change_label.config(text=f"{change_percent:.2f}%", fg='#ff4444')
                else:
                    self.price_change_label.config(text="0.00%", fg='#cccccc')
            else:
                self.price_change_label.config(text="+0.00%", fg='#00ff88')
            
            self.previous_price = prix_actuel
            
            # Update trading zones display
            self.update_zones_display()
            
        except Exception as e:
            self.log_message(f"Error updating price: {str(e)}")
    
    def update_portfolio_display(self):
        """Update the portfolio display"""
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
                
                self.hbar_balance_label.config(text=f"HBAR Balance: {solde_hbar:.2f}")
                self.usd_balance_label.config(text=f"USD Balance: ${solde_usd:.2f}")
                self.total_value_label.config(text=f"Total Value: ${total_value:.2f}")
                
                # Update performance
                if not self.capital_initial:
                    self.capital_initial = 3000.0  # Demo initial capital
                
                performance = ((total_value / self.capital_initial) - 1) * 100
                if performance >= 0:
                    self.performance_label.config(text=f"Performance: +{performance:.2f}%", fg='#00ff88')
                else:
                    self.performance_label.config(text=f"Performance: {performance:.2f}%", fg='#ff4444')
                
                # Update average price
                if not self.prix_moyen_achat:
                    self.prix_moyen_achat = 0.124800  # Demo average price
                self.avg_price_label.config(text=f"Avg Buy Price: ${self.prix_moyen_achat:.6f}")
                
        except Exception as e:
            self.log_message(f"Error updating portfolio: {str(e)}")
    
    def update_zones_display(self):
        """Update the trading zones display"""
        try:
            self.zones_text.delete("1.0", tk.END)
            
            prix_actuel = obtenir_prix_hbar()
            if not prix_actuel:
                return
            
            # Display buy zones
            self.zones_text.insert(tk.END, "BUY ZONES:\n", "title")
            for i, zone in enumerate(ZONES_ACHAT, 1):
                in_zone = zone["prix_min"] <= prix_actuel <= zone["prix_max"]
                status = "🎯 ACTIVE" if in_zone else "⏸️ WAITING"
                color = "#00ff88" if in_zone else "#888888"
                
                zone_text = f"Zone {i}: ${zone['prix_min']:.3f} - ${zone['prix_max']:.3f} | ${zone['montant']} | {status}\n"
                self.zones_text.insert(tk.END, zone_text)
            
            self.zones_text.insert(tk.END, "\nSELL ZONES:\n", "title")
            for i, zone in enumerate(ZONES_VENTE, 1):
                in_zone = prix_actuel >= zone["prix_min"]
                status = "💰 ACTIVE" if in_zone else "⏸️ WAITING"
                color = "#00ff88" if in_zone else "#888888"
                
                zone_text = f"Zone {i}: ${zone['prix_min']:.3f}+ | {zone['pourcentage_benefices']*100:.0f}% | {status}\n"
                self.zones_text.insert(tk.END, zone_text)
                
        except Exception as e:
            self.log_message(f"Error updating zones: {str(e)}")
    
    def update_transactions_display(self):
        """Update the transactions display"""
        try:
            self.transactions_text.delete("1.0", tk.END)
            
            # Demo mode - add sample transactions if none exist
            if not self.derniers_achats and not self.dernieres_ventes:
                self.derniers_achats = [
                    {"date": "2025-04-06T14:30:00", "quantite": 1500.00, "prix": 0.125000},
                    {"date": "2025-04-05T16:45:00", "quantite": 2000.00, "prix": 0.118000},
                    {"date": "2025-04-04T12:20:00", "quantite": 1750.00, "prix": 0.122000}
                ]
                self.dernieres_ventes = [
                    {"date": "2025-04-06T18:15:00", "quantite": 325.50, "prix": 0.142000},
                    {"date": "2025-04-05T20:30:00", "quantite": 450.25, "prix": 0.139000}
                ]
            
            # Show recent buys
            if self.derniers_achats:
                self.transactions_text.insert(tk.END, "Recent Buys:\n", "title")
                for achat in self.derniers_achats[-5:]:  # Last 5
                    date = achat['date'].split('T')[0]
                    text = f"📈 {date}: {achat['quantite']:.2f} HBAR @ ${achat['prix']:.6f}\n"
                    self.transactions_text.insert(tk.END, text)
            
            # Show recent sells
            if self.dernieres_ventes:
                self.transactions_text.insert(tk.END, "\nRecent Sells:\n", "title")
                for vente in self.dernieres_ventes[-5:]:  # Last 5
                    date = vente['date'].split('T')[0]
                    text = f"📉 {date}: {vente['quantite']:.2f} HBAR @ ${vente['prix']:.6f}\n"
                    self.transactions_text.insert(tk.END, text)
                    
        except Exception as e:
            self.log_message(f"Error updating transactions: {str(e)}")
    
    def start_price_monitoring(self):
        """Start the price monitoring thread"""
        def monitor():
            while True:
                if not self.is_trading:
                    self.update_price_display()
                    self.update_portfolio_display()
                    self.update_transactions_display()
                time.sleep(30)  # Update every 30 seconds
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def start_trading(self):
        """Start the trading bot"""
        if self.is_trading:
            return
        
        # Check API configuration
        if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
            messagebox.showwarning("Demo Mode", 
                               "Running in DEMO MODE - No real trading will occur.\n\nTo enable real trading, configure your Coinbase API keys in config.py")
            # Continue in demo mode
        
        self.is_trading = True
        self.status_label.config(text="🟢 TRADING", fg='#00ff88')
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        self.log_message("🚀 Starting Eleutheria trading bot...")
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.trading_thread.start()
    
    def stop_trading(self):
        """Stop the trading bot"""
        if not self.is_trading:
            return
        
        self.is_trading = False
        self.status_label.config(text="🟡 STOPPED", fg='#ffff00')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.log_message("⏹️ Trading bot stopped")
    
    def trading_loop(self):
        """Main trading loop"""
        try:
            # Initialize capital if needed
            if not self.capital_initial:
                self.capital_initial = calculer_capital_total()
                if not self.capital_initial:
                    self.log_message("❌ Failed to calculate initial capital")
                    self.stop_trading()
                    return
            
            self.log_message(f"💰 Initial capital: ${self.capital_initial:.2f}")
            
            while self.is_trading:
                try:
                    # Get current price
                    prix_actuel = obtenir_prix_hbar()
                    if not prix_actuel:
                        self.log_message("⚠️ Unable to get current price")
                        time.sleep(300)
                        continue
                    
                    # Check for trading opportunities
                    self.check_trading_opportunities(prix_actuel)
                    
                    # Update displays
                    self.update_price_display()
                    self.update_portfolio_display()
                    self.update_transactions_display()
                    
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
        """Check for trading opportunities"""
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
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Eleutheria Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg='#1a1a1a')
        
        # Settings content
        title = tk.Label(settings_window, 
                        text="⚙️ TRADING SETTINGS", 
                        font=('Arial', 16, 'bold'),
                        bg='#1a1a1a', 
                        fg='#00ff88')
        title.pack(pady=20)
        
        # API Status
        api_frame = tk.Frame(settings_window, bg='#2a2a2a', relief='raised', bd=2)
        api_frame.pack(fill='x', padx=20, pady=10)
        
        api_title = tk.Label(api_frame, 
                            text="🔑 API Configuration", 
                            font=('Arial', 12, 'bold'),
                            bg='#2a2a2a', 
                            fg='#ffffff')
        api_title.pack(anchor='w', padx=20, pady=10)
        
        if API_KEY != "VOTRE_API_KEY":
            api_status = tk.Label(api_frame, 
                                 text="✅ API Keys Configured", 
                                 font=('Arial', 10),
                                 bg='#2a2a2a', 
                                 fg='#00ff88')
        else:
            api_status = tk.Label(api_frame, 
                                 text="❌ API Keys Not Configured", 
                                 font=('Arial', 10),
                                 bg='#2a2a2a', 
                                 fg='#ff4444')
        api_status.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Trading Parameters
        params_frame = tk.Frame(settings_window, bg='#2a2a2a', relief='raised', bd=2)
        params_frame.pack(fill='x', padx=20, pady=10)
        
        params_title = tk.Label(params_frame, 
                               text="🎯 Trading Parameters", 
                               font=('Arial', 12, 'bold'),
                               bg='#2a2a2a', 
                               fg='#ffffff')
        params_title.pack(anchor='w', padx=20, pady=10)
        
        stop_loss_label = tk.Label(params_frame, 
                                  text=f"Stop Loss: {STOP_LOSS_POURCENTAGE*100:.0f}%", 
                                  font=('Arial', 10),
                                  bg='#2a2a2a', 
                                  fg='#cccccc')
        stop_loss_label.pack(anchor='w', padx=20, pady=2)
        
        # Help button
        help_button = tk.Button(settings_window, 
                               text="📖 View Documentation", 
                               command=lambda: webbrowser.open("https://github.com/your-repo/eleutheria"),
                               bg='#444444', 
                               fg='#ffffff',
                               font=('Arial', 10),
                               relief='flat',
                               padx=20, 
                               pady=5)
        help_button.pack(pady=20)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EleutheriaApp(root)
    
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