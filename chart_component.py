#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Chart Component for Eleutheria Desktop App
Displays price history using tkinter canvas
"""

import tkinter as tk
from datetime import datetime, timedelta
import math

class PriceChart:
    def __init__(self, parent, width=400, height=200):
        self.parent = parent
        self.width = width
        self.height = height
        self.price_history = []
        self.max_points = 50
        
        # Create canvas
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Draw initial grid
        self.draw_grid()
    
    def add_price(self, price, timestamp=None):
        """Add a new price point to the chart"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.price_history.append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Keep only the last max_points
        if len(self.price_history) > self.max_points:
            self.price_history = self.price_history[-self.max_points:]
        
        self.redraw()
    
    def draw_grid(self):
        """Draw the background grid"""
        self.canvas.delete("grid")
        
        # Vertical lines (time)
        for i in range(0, self.width, 50):
            self.canvas.create_line(i, 0, i, self.height, 
                                   fill='#333333', tags="grid")
        
        # Horizontal lines (price)
        for i in range(0, self.height, 40):
            self.canvas.create_line(0, i, self.width, i, 
                                   fill='#333333', tags="grid")
    
    def redraw(self):
        """Redraw the price chart"""
        if len(self.price_history) < 2:
            return
        
        self.canvas.delete("chart")
        
        # Find price range
        prices = [p['price'] for p in self.price_history]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        # Calculate points
        points = []
        for i, data in enumerate(self.price_history):
            x = (i / (len(self.price_history) - 1)) * (self.width - 40) + 20
            y = self.height - 20 - ((data['price'] - min_price) / price_range) * (self.height - 40)
            points.append(x)
            points.append(y)
        
        # Draw price line
        if len(points) >= 4:
            self.canvas.create_line(points, fill='#00ff88', width=2, tags="chart")
        
        # Draw price points
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            self.canvas.create_oval(x-2, y-2, x+2, y+2, 
                                   fill='#00ff88', tags="chart")
        
        # Draw price labels
        self.canvas.delete("labels")
        if len(self.price_history) > 0:
            current_price = self.price_history[-1]['price']
            self.canvas.create_text(self.width - 10, 10, 
                                   text=f"${current_price:.6f}", 
                                   fill='#00ff88', anchor='e', 
                                   font=('Arial', 10, 'bold'), tags="labels")
            
            # Show min/max prices
            self.canvas.create_text(10, 10, 
                                   text=f"Max: ${max_price:.6f}", 
                                   fill='#00ff88', anchor='w', 
                                   font=('Arial', 8), tags="labels")
            self.canvas.create_text(10, self.height - 10, 
                                   text=f"Min: ${min_price:.6f}", 
                                   fill='#00ff88', anchor='w', 
                                   font=('Arial', 8), tags="labels")
    
    def clear(self):
        """Clear the chart"""
        self.price_history = []
        self.canvas.delete("all")
        self.draw_grid() 