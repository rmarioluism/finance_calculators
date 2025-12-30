import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
from functools import reduce
import time

import matplotlib as mpl

import os
from contextlib import redirect_stdout, redirect_stderr
from finance_calculators.portfolio_simulation import Portfolio

# Set global default font size for x and y tick labels
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['axes.labelsize'] = 20

import copy
pd.options.mode.copy_on_write = True


portofolio_strategies = [
                         {"name":f"{stock}/{bond}%",
                         'tickers': ["VTSAX","VBTLX", "VYM"],
                         'weights': [stock/100, bond/100, 20/100],
                         "comment":""} for stock, bond in zip(range(0,90,10),reversed(range(0,90,10)))
                         ]


