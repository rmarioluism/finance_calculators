import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
from functools import reduce

import matplotlib as mpl
from finance_calculators.portfolio_simulation import Portfolio

# Set global default font size for x and y tick labels
fontsize = 10
mpl.rcParams['xtick.labelsize'] = fontsize
mpl.rcParams['ytick.labelsize'] = fontsize
mpl.rcParams['axes.labelsize'] = fontsize

import copy

pd.options.mode.copy_on_write = True

portofolio_strategies = [
                         {"name":"3 Fund",
                         'tickers': ["VTSAX","VBTLX", "VYM"],
                         'weights': [.5, .2, .3],
                         "comment":""} 
                         ]

portfolio_obj = Portfolio(portofolio_strategies)
portfolio_obj.download_portfolio_historical_data()
portfolio_outcomes = portfolio_obj.simulate_dca_on_historical_data(purchase_amount = 10_000, trim_method = 2000, N=8, plot_mix=False)

portofolio_strategies = [
                         {"name":f"{stock}/{bond}%",
                         'tickers': ["VTSAX","VBTLX"],
                         'weights': [stock/100, bond/100,],
                         "comment":""} for stock, bond in zip(range(0,101,10),reversed(range(0,101,10)))
                         ]

portfolio_obj = Portfolio(portofolio_strategies)
portfolio_obj.download_portfolio_historical_data()
portfolio_outcomes = portfolio_obj.simulate_dca_on_historical_data(purchase_amount = 10_000, trim_method = 2000, N=10, plot_mix=True)


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration
COLORS = {"year": "#002C3E", "month": "#BC0E4C", "day": "#FFC501"}
plt.figure(figsize=(12, 7))

# Data Extraction
labels = [p["name"].replace("%", "") for p in portfolio_outcomes]
indices = range(len(portfolio_outcomes))

# Track min/max for dynamic scaling to keep text inside
y_min_coords = []
y_max_coords = []

for i, p in enumerate(portfolio_outcomes):
    stats = p["best_worst_year"][0]
    equity_m = p["equity"] / 1e6
    
    # Values as percentages
    b_year, w_year = stats['best year'] * 100, stats['worst year'] * 100
    b_month, w_month = stats['best month'] * 100, stats['worst month'] * 100
    b_day, w_day = stats['best day'] * 100, stats['worst day'] * 100
    up, down = stats["up market"], stats["down market"]

    # Record coordinates for auto-scaling (including label offsets)
    y_max_coords.append(b_year + 8) # Padding for the $M label
    y_min_coords.append(w_year - 5) # Padding for the % label

    # 1. Plot Bars
    plt.bar(i, b_year, color=COLORS["year"])
    plt.bar(i, w_year, color=COLORS["year"])
    plt.bar(i, b_month, color=COLORS["month"])
    plt.bar(i, w_month, color=COLORS["month"])
    plt.bar(i, b_day, color=COLORS["day"])
    plt.bar(i, w_day, color=COLORS["day"])

    # 2. Add Text Labels
    # Best Year %
    plt.text(i, b_year + 1, f'{b_year:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Up/Down Market Ratio
    plt.text(i, b_year - 4, f'{up}/{up + down}', color="white", ha='center', va='bottom', fontweight='bold', fontsize=8)

    # Equity ($M) - Highest text element
    plt.text(i, b_year + 5, f'${equity_m:.2f}M', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Worst Year % - Lowest text element
    plt.text(i, w_year - 1, f'{w_year:.1f}%', ha='center', va='top', fontweight='bold', color='red', fontsize=9)

# Formatting
plt.xticks(indices, labels, rotation=45, ha='right')
plt.xlabel("Stock/Bond", fontweight='bold', labelpad=10) # Added x-label
plt.ylabel("Return (%)", fontweight='bold')
plt.axhline(0, color='black', linewidth=0.8)

# Set Y-limits with buffer to ensure text is "within"
plt.ylim(min(y_min_coords), max(y_max_coords))

# 3. Legend
legend_handles = [
    mpatches.Patch(color=COLORS["year"], label='Yearly'),
    mpatches.Patch(color=COLORS["month"], label='Monthly'),
    mpatches.Patch(color=COLORS["day"], label='Daily')
]
plt.legend(handles=legend_handles, loc='upper left')

plt.tight_layout()
plt.show()

#TODO add the three color legend
# TODO Add total return in millions or thousands