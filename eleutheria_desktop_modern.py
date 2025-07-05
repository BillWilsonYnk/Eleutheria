#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eleutheria Desktop Trading App - Modern Material Design
A beautiful, modern desktop application for automated HBAR trading on Coinbase
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

class ModernButton(tk.Canvas):
    """Modern Material Design button with hover effects"""
    def __init__(self, parent, text, command=None, bg="#2196F3", fg="white", 
                 hover_bg="#1976D2", width=120, height=40, font_size=12, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.font_size = font_size
        self.state = "normal"
        
        # Create button shape
        self.draw_button()
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        # Add text
        self.create_text(width//2, height//2, text=text, fill=fg, 
                        font=('Segoe UI', font_size, 'bold'))
    
    def draw_button(self):
        """Draw the button with rounded corners and shadow"""
        self.delete("all")
        
        # Shadow
        shadow_color = "#CCCCCC"
        self.create_rounded_rectangle(3, 3, self.winfo_reqwidth()-3, self.winfo_reqheight()-3, 
                                     radius=8, fill=shadow_color)
        
        # Button
        color = self.hover_bg if self.state == "hover" else self.bg
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth()-6, self.winfo_reqheight()-6, 
                                     radius=8, fill=color)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=8, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.state = "hover"
        self.draw_button()
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.itemcget(1, "text"), fill=self.fg, 
                        font=('Segoe UI', self.font_size, 'bold'))
    
    def on_leave(self, event):
        self.state = "normal"
        self.draw_button()
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.itemcget(1, "text"), fill=self.fg, 
                        font=('Segoe UI', self.font_size, 'bold'))
    
    def on_click(self, event):
        self.state = "pressed"
        self.draw_button()
    
    def on_release(self, event):
        self.state = "hover"
        self.draw_button()
        if self.command:
            self.command()

class ModernCard(tk.Frame):
    """Modern Material Design card with shadow and rounded corners"""
    def __init__(self, parent, title="", bg="#FFFFFF", fg="#212121", **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), **kwargs)
        
        # Create card container
        self.card_frame = tk.Frame(self, bg=bg, relief="flat", bd=0)
        self.card_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add shadow effect
        self.shadow_frame = tk.Frame(self, bg="#E0E0E0", relief="flat", bd=0)
        self.shadow_frame.place(x=2, y=2, relwidth=1, relheight=1)
        self.shadow_frame.lower()
        
        # Title
        if title:
            title_label = tk.Label(self.card_frame, text=title, 
                                  font=('Segoe UI', 14, 'bold'),
                                  bg=bg, fg=fg)
            title_label.pack(anchor='w', padx=20, pady=(15, 10))
            
            # Separator
            separator = tk.Frame(self.card_frame, height=1, bg="#E0E0E0")
            separator.pack(fill='x', padx=20, pady=(0, 10))

class PriceDisplay(tk.Frame):
    """Modern price display with animations"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), **kwargs)
        
        # Price label
        self.price_label = tk.Label(self, text="$0.000000", 
                                   font=('Segoe UI', 32, 'bold'),
                                   bg=self.cget('bg'), fg="#4CAF50")
        self.price_label.pack()
        
        # Change label
        self.change_label = tk.Label(self, text="+0.00%", 
                                    font=('Segoe UI', 14),
                                    bg=self.cget('bg'), fg="#4CAF50")
        self.change_label.pack()
        
        self.previous_price = None
    
    def update_price(self, price, change_percent=0):
        """Update price with animation"""
        self.price_label.config(text=f"${price:.6f}")
        
        # Color based on change
        if change_percent > 0:
            color = "#4CAF50"  # Green
        elif change_percent < 0:
            color = "#F44336"  # Red
        else:
            color = "#757575"  # Gray
        
        self.price_label.config(fg=color)
        self.change_label.config(text=f"{change_percent:+.2f}%", fg=color)

class ModernProgressBar(tk.Canvas):
    """Modern progress bar with animation"""
    def __init__(self, parent, width=200, height=8, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.progress = 0
        
        # Background
        self.create_rounded_rectangle(0, 0, width, height, radius=4, fill="#E0E0E0")
        
        # Progress bar
        self.progress_bar = self.create_rounded_rectangle(0, 0, 0, height, 
                                                        radius=4, fill="#4CAF50")
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=4, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def set_progress(self, progress):
        """Set progress (0-100) with animation"""
        self.progress = max(0, min(100, progress))
        width = (self.progress / 100) * self.width
        
        # Animate
        current_width = self.coords(self.progress_bar)[2]
        step = (width - current_width) / 10
        
        def animate():
            current = self.coords(self.progress_bar)[2]
            if abs(current - width) > 1:
                new_width = current + step
                self.coords(self.progress_bar, 0, 0, new_width, self.height)
                self.after(20, animate)
            else:
                self.coords(self.progress_bar, 0, 0, width, self.height)
        
        animate()

class EleutheriaModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eleutheria - Modern Trading Bot")
        self.root.geometry("1400x900")
        self.root.configure(bg='#FAFAFA')  # Light Material Design background
        
        # Set window icon and properties
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
        """Create the main UI widgets with Material Design"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#FAFAFA')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with gradient effect
        self.create_header(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#FAFAFA')
        content_frame.pack(fill='both', expand=True, pady=20)
        
        # Left panel - Market data
        self.create_market_panel(content_frame)
        
        # Right panel - Trading info
        self.create_trading_panel(content_frame)
        
        # Bottom panel - Logs
        self.create_log_panel(main_frame)
    
    def create_header(self, parent):
        """Create modern header with gradient effect"""
        header_frame = tk.Frame(parent, bg='#2196F3', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title with modern typography
        title_label = tk.Label(header_frame, 
                              text="⚡ ELEUTHERIA", 
                              font=('Segoe UI', 28, 'bold'),
                              bg='#2196F3', 
                              fg='white')
        title_label.pack(side='left', padx=30, pady=20)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Modern Automated Trading", 
                                 font=('Segoe UI', 14),
                                 bg='#2196F3', 
                                 fg='#E3F2FD')
        subtitle_label.pack(side='left', padx=(10, 0), pady=20)
        
        # Status indicator
        self.status_label = tk.Label(header_frame, 
                                    text="🟡 READY", 
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='#2196F3', 
                                    fg='#FFF59D')
        self.status_label.pack(side='right', padx=30, pady=20)
    
    def create_control_panel(self, parent):
        """Create modern control panel"""
        control_frame = ModernCard(parent, title="Trading Controls")
        control_frame.pack(fill='x', pady=(0, 20))
        
        # Button container
        button_frame = tk.Frame(control_frame.card_frame, bg=control_frame.card_frame.cget('bg'))
        button_frame.pack(pady=20)
        
        # Modern buttons
        self.start_button = ModernButton(button_frame, 
                                        text="🚀 START TRADING", 
                                        command=self.start_trading,
                                        bg="#4CAF50", 
                                        hover_bg="#388E3C",
                                        width=150, 
                                        height=45,
                                        font_size=12)
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = ModernButton(button_frame, 
                                       text="⏹️ STOP TRADING", 
                                       command=self.stop_trading,
                                       bg="#F44336", 
                                       hover_bg="#D32F2F",
                                       width=150, 
                                       height=45,
                                       font_size=12)
        self.stop_button.pack(side='left', padx=10)
        
        self.settings_button = ModernButton(button_frame, 
                                           text="⚙️ SETTINGS", 
                                           command=self.open_settings,
                                           bg="#FF9800", 
                                           hover_bg="#F57C00",
                                           width=120, 
                                           height=45,
                                           font_size=12)
        self.settings_button.pack(side='left', padx=10)
        
        # Initially disable stop button
        self.stop_button.config(state='disabled')
    
    def create_market_panel(self, parent):
        """Create modern market data panel"""
        market_frame = ModernCard(parent, title="📊 Market Data")
        market_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Price display
        self.price_display = PriceDisplay(market_frame)
        self.price_display.pack(pady=20)
        
        # Stats grid
        stats_frame = tk.Frame(market_frame.card_frame, bg=market_frame.card_frame.cget('bg'))
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # 24h stats
        self.high_24h_label = tk.Label(stats_frame, 
                                      text="24h High: $0.000000", 
                                      font=('Segoe UI', 11),
                                      bg=stats_frame.cget('bg'), 
                                      fg="#4CAF50")
        self.high_24h_label.pack(anchor='w', pady=2)
        
        self.low_24h_label = tk.Label(stats_frame, 
                                     text="24h Low: $0.000000", 
                                     font=('Segoe UI', 11),
                                     bg=stats_frame.cget('bg'), 
                                     fg="#F44336")
        self.low_24h_label.pack(anchor='w', pady=2)
        
        # Trading zones
        zones_frame = tk.Frame(market_frame.card_frame, bg=market_frame.card_frame.cget('bg'))
        zones_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        zones_title = tk.Label(zones_frame, 
                              text="🎯 Trading Zones", 
                              font=('Segoe UI', 14, 'bold'),
                              bg=zones_frame.cget('bg'), 
                              fg="#212121")
        zones_title.pack(anchor='w', pady=(0, 10))
        
        # Create zones display with modern styling
        self.zones_text = scrolledtext.ScrolledText(zones_frame, 
                                                   height=8, 
                                                   bg='#F5F5F5', 
                                                   fg='#212121',
                                                   font=('Consolas', 10),
                                                   relief='flat',
                                                   borderwidth=0)
        self.zones_text.pack(fill='both', expand=True, pady=5)
        self.update_zones_display()
    
    def create_trading_panel(self, parent):
        """Create modern trading information panel"""
        trading_frame = ModernCard(parent, title="💰 Trading Portfolio")
        trading_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Portfolio info with modern cards
        portfolio_frame = tk.Frame(trading_frame.card_frame, bg=trading_frame.card_frame.cget('bg'))
        portfolio_frame.pack(fill='x', padx=20, pady=10)
        
        # Balance cards
        self.create_balance_card(portfolio_frame, "HBAR Balance", "0.00", "#4CAF50")
        self.create_balance_card(portfolio_frame, "USD Balance", "$0.00", "#2196F3")
        self.create_balance_card(portfolio_frame, "Total Value", "$0.00", "#FF9800")
        
        # Performance section
        perf_frame = tk.Frame(trading_frame.card_frame, bg=trading_frame.card_frame.cget('bg'))
        perf_frame.pack(fill='x', padx=20, pady=10)
        
        self.performance_label = tk.Label(perf_frame, 
                                         text="Performance: +0.00%", 
                                         font=('Segoe UI', 16, 'bold'),
                                         bg=perf_frame.cget('bg'), 
                                         fg="#4CAF50")
        self.performance_label.pack(anchor='w', pady=5)
        
        self.avg_price_label = tk.Label(perf_frame, 
                                       text="Avg Buy Price: $0.000000", 
                                       font=('Segoe UI', 12),
                                       bg=perf_frame.cget('bg'), 
                                       fg="#757575")
        self.avg_price_label.pack(anchor='w', pady=2)
        
        # Progress bar for performance
        self.progress_bar = ModernProgressBar(perf_frame, width=300, height=10)
        self.progress_bar.pack(anchor='w', pady=10)
        
        # Recent transactions
        trans_frame = tk.Frame(trading_frame.card_frame, bg=trading_frame.card_frame.cget('bg'))
        trans_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        trans_title = tk.Label(trans_frame, 
                              text="📈 Recent Transactions", 
                              font=('Segoe UI', 14, 'bold'),
                              bg=trans_frame.cget('bg'), 
                              fg="#212121")
        trans_title.pack(anchor='w', pady=(0, 10))
        
        self.transactions_text = scrolledtext.ScrolledText(trans_frame, 
                                                          height=8, 
                                                          bg='#F5F5F5', 
                                                          fg='#212121',
                                                          font=('Consolas', 10),
                                                          relief='flat',
                                                          borderwidth=0)
        self.transactions_text.pack(fill='both', expand=True, pady=5)
    
    def create_balance_card(self, parent, title, value, color):
        """Create a modern balance card"""
        card = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=1)
        card.pack(fill='x', pady=5)
        
        title_label = tk.Label(card, text=title, 
                              font=('Segoe UI', 11),
                              bg='#FFFFFF', fg='#757575')
        title_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        value_label = tk.Label(card, text=value, 
                              font=('Segoe UI', 16, 'bold'),
                              bg='#FFFFFF', fg=color)
        value_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        # Store reference for updates
        if title == "HBAR Balance":
            self.hbar_balance_label = value_label
        elif title == "USD Balance":
            self.usd_balance_label = value_label
        elif title == "Total Value":
            self.total_value_label = value_label
    
    def create_log_panel(self, parent):
        """Create modern log panel"""
        log_frame = ModernCard(parent, title="📝 Trading Activity")
        log_frame.pack(fill='x', pady=(20, 0))
        
        # Log text area with modern styling
        self.log_text = scrolledtext.ScrolledText(log_frame.card_frame, 
                                                 height=6, 
                                                 bg='#F5F5F5', 
                                                 fg='#212121',
                                                 font=('Consolas', 10),
                                                 relief='flat',
                                                 borderwidth=0)
        self.log_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Clear log button
        clear_button = ModernButton(log_frame.card_frame, 
                                   text="🗑️ Clear Log", 
                                   command=self.clear_log,
                                   bg="#757575", 
                                   hover_bg="#616161",
                                   width=100, 
                                   height=35,
                                   font_size=10)
        clear_button.pack(anchor='w', padx=20, pady=(0, 20))
    
    def log_message(self, message):
        """Add a message to the log with modern styling"""
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
        """Update the price display with animations"""
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
        """Update the portfolio display with modern styling"""
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
                
                self.hbar_balance_label.config(text=f"{solde_hbar:.2f}")
                self.usd_balance_label.config(text=f"${solde_usd:.2f}")
                self.total_value_label.config(text=f"${total_value:.2f}")
                
                # Update performance
                if not self.capital_initial:
                    self.capital_initial = 3000.0  # Demo initial capital
                
                performance = ((total_value / self.capital_initial) - 1) * 100
                if performance >= 0:
                    self.performance_label.config(text=f"Performance: +{performance:.2f}%", fg="#4CAF50")
                else:
                    self.performance_label.config(text=f"Performance: {performance:.2f}%", fg="#F44336")
                
                # Update progress bar
                self.progress_bar.set_progress(max(0, min(100, performance + 50)))
                
                # Update average price
                if not self.prix_moyen_achat:
                    self.prix_moyen_achat = 0.124800  # Demo average price
                self.avg_price_label.config(text=f"Avg Buy Price: ${self.prix_moyen_achat:.6f}")
                
        except Exception as e:
            self.log_message(f"Error updating portfolio: {str(e)}")
    
    def update_zones_display(self):
        """Update the trading zones display with modern styling"""
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
    
    def update_transactions_display(self):
        """Update the transactions display with modern styling"""
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
        """Start the trading bot with modern UI feedback"""
        if self.is_trading:
            return
        
        # Check API configuration
        if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
            messagebox.showwarning("Demo Mode", 
                               "Running in DEMO MODE - No real trading will occur.\n\nTo enable real trading, configure your Coinbase API keys in config.py")
            # Continue in demo mode
        
        self.is_trading = True
        self.status_label.config(text="🟢 TRADING", fg='#4CAF50')
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        self.log_message("🚀 Starting Eleutheria modern trading bot...")
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.trading_thread.start()
    
    def stop_trading(self):
        """Stop the trading bot with modern UI feedback"""
        if not self.is_trading:
            return
        
        self.is_trading = False
        self.status_label.config(text="🟡 STOPPED", fg='#FF9800')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.log_message("⏹️ Trading bot stopped")
    
    def trading_loop(self):
        """Main trading loop with modern error handling"""
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
        """Check for trading opportunities with modern logging"""
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
        """Open modern settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Eleutheria Settings")
        settings_window.geometry("700x500")
        settings_window.configure(bg='#FAFAFA')
        
        # Settings content with modern styling
        title = tk.Label(settings_window, 
                        text="⚙️ TRADING SETTINGS", 
                        font=('Segoe UI', 20, 'bold'),
                        bg='#FAFAFA', 
                        fg='#2196F3')
        title.pack(pady=30)
        
        # API Status card
        api_card = ModernCard(settings_window, title="🔑 API Configuration")
        api_card.pack(fill='x', padx=20, pady=10)
        
        if API_KEY != "VOTRE_API_KEY":
            api_status = tk.Label(api_card.card_frame, 
                                 text="✅ API Keys Configured", 
                                 font=('Segoe UI', 12),
                                 bg=api_card.card_frame.cget('bg'), 
                                 fg='#4CAF50')
        else:
            api_status = tk.Label(api_card.card_frame, 
                                 text="❌ API Keys Not Configured", 
                                 font=('Segoe UI', 12),
                                 bg=api_card.card_frame.cget('bg'), 
                                 fg='#F44336')
        api_status.pack(pady=20)
        
        # Trading Parameters card
        params_card = ModernCard(settings_window, title="🎯 Trading Parameters")
        params_card.pack(fill='x', padx=20, pady=10)
        
        stop_loss_label = tk.Label(params_card.card_frame, 
                                  text=f"Stop Loss: {STOP_LOSS_POURCENTAGE*100:.0f}%", 
                                  font=('Segoe UI', 12),
                                  bg=params_card.card_frame.cget('bg'), 
                                  fg='#212121')
        stop_loss_label.pack(pady=10)
        
        # Help button
        help_button = ModernButton(settings_window, 
                                  text="📖 View Documentation", 
                                  command=lambda: webbrowser.open("https://github.com/your-repo/eleutheria"),
                                  bg="#2196F3", 
                                  hover_bg="#1976D2",
                                  width=200, 
                                  height=40,
                                  font_size=12)
        help_button.pack(pady=30)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EleutheriaModernApp(root)
    
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