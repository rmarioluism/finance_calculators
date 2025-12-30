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
                         {"name":f"{stock}/{bond}%",
                         'tickers': ["VTSAX","VBTLX", "VYM"],
                         'weights': [stock/100, bond/100, 20/100],
                         "comment":""} for stock, bond in zip(range(0,100,10),reversed(range(0,100,10)))
                         ]

portfolio_obj = Portfolio(portofolio_strategies)
portfolio_obj.download_portfolio_historical_data()
portfolio_outcomes = portfolio_obj.simulate_dca_on_historical_data(purchase_amount = 10_000, trim_method = 2000, N=8)


plt.figure(figsize=(10, 6))

labels = [p["name"].replace("%","") for p in portfolio_outcomes]
indices = range(len(portfolio_outcomes))

best_day = []
worst_day = []
best_month = []
worst_month = []
best_year = []
worst_year = []
for i, p in enumerate(portfolio_outcomes):
    best_day.append(p["best_worst_year"][0]['best day'] * 100)
    worst_day.append(p["best_worst_year"][0]['worst day'] * 100)
    best_month.append(p["best_worst_year"][0]['best month'] * 100)
    worst_month.append(p["best_worst_year"][0]['worst month'] * 100)
    best_year.append(p["best_worst_year"][0]['best year'] * 100)
    worst_year.append(p["best_worst_year"][0]['worst year'] * 100)

plt.bar(indices, best_year, color="#002C3E")
plt.bar(indices, worst_year, color="#002C3E")
# plt.bar(indices, best_month, color="#BC0E4C", )
# plt.bar(indices, worst_month, color="#BC0E4C")
# plt.bar(indices, best_day, color="#FFC501")
# plt.bar(indices, worst_day, color="#FFC501")



for i, p in enumerate(portfolio_outcomes):
    best_val = p["best_worst_year"][0]['best year'] * 100
    worst_val = p["best_worst_year"][0]['worst year'] * 100
    up_market = p["best_worst_year"][0]["up market"]
    down_market = p["best_worst_year"][0]["down market"]
    equity = p["equity"]

    # Text for Best Year (on top)
    plt.text(i, best_val + 1, f'{best_val:.1f}%',
             ha='center', va='bottom', fontweight='bold')

    # Text for Best Year (on top)
    plt.text(i, best_val + 4, f'${equity/1e6:.02f}M',
             ha='center', va='bottom', fontweight='bold')

    plt.text(i, 1, f'{up_market}/{up_market+down_market}',
             color="white",
             ha='center', va='bottom', fontweight='bold')

    # Text for Worst Year (underneath)
    plt.text(i, worst_val - 1, f'{worst_val:.1f}%',
             ha='center', va='top', fontweight='bold', color='red')

plt.xticks(indices, labels, rotation=90, ha='right')
plt.axhline(0, color='black', linewidth=0.8) # Add a baseline at 0%
plt.ylabel("Return (%)")
# plt.title("Best and Worst Year Outcomes by Portfolio")
plt.tight_layout()
plt.show()

#TODO add the three color legend
# TODO Add total return in millions or thousands