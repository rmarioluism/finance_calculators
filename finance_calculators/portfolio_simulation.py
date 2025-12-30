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

# Set global default font size for x and y tick labels
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['axes.labelsize'] = 20

import copy
pd.options.mode.copy_on_write = True


class Portfolio():

    def __init__(self, portofolio_strategies=()):
        self.download_cache = {}
        self.portofolio_strategies = portofolio_strategies
        self.info_cache = {}
        self.max_len = 0
        self.min_len = 1e6
        self.date_index = None
        self.earliest_date = None

        self.details = {"yield":"APY","annualReportExpenseRatio":"expense",
                    "symbol":"ticker","dividendRate":"dividendRate",
                    "longName":"longName","ytdReturn":"ytdReturn",
                    "annualHoldingsTurnover":"turnOver","trailingPE":"trailingPE",
                    "beta3Year":"beta3Year", "netExpenseRatio":"netExpenseRatio"}
        
    def download(self,):
        # Download and cache the data for each ticker including detailes about expenses, etc...
        for  vals in self.portofolio_strategies:
            for ticker in vals["tickers"]:
                if ticker not in self.download_cache:
                    with open(os.devnull, 'w') as fnull:
                        with redirect_stdout(fnull), redirect_stderr(fnull):
                            data = yf.download(ticker, period="max")
                            data.columns = data.columns.droplevel(1)

                            # idx = np.random.randint(5,11,1).item()
                            # data = data[-idx:]
                            # Store data of oldest fund to pad all other to the same size
                            if data.shape[0]>self.max_len:
                                dummy_data = copy.deepcopy(data)
                                self.max_len = data.shape[0]

                            if data.shape[0]<self.min_len:
                                self.min_len = data.shape[0]
                                self.earliest_date = data.index[0]

                            self.download_cache[ticker] = copy.deepcopy(data)

                            info_data   = yf.Ticker(ticker)
                            self.info_cache[ticker] = {n:info_data.info.get(t) for t,n in self.details.items()}

        # Pad all funds to the size of the longest
        for key in self.download_cache.keys():
            merged_df = dummy_data.merge(self.download_cache[key],
                                        left_index=True,
                                        right_index=True,
                                        how='outer',
                                        suffixes=('_1', '_2'))

            merged_df = merged_df.iloc[:,5:]
            merged_df.columns = self.download_cache[key].columns
            merged_df = merged_df.bfill().ffill()
            self.download_cache[key] = merged_df


    def simulate_dca_on_historical_data(self,purchase_amount = 10_000, trim_method = 2000):
        plt.figure(figsize=(16,8))

        portfolio_outcomes = []
        plotted = []
        
        # Plot the fund price history and compute the equity of DCA
        for  vals in self.portofolio_strategies:
            name, tickers, weights,_ = vals.values()

            portfolio = []
            expenses = 0
            portfolio_historical_price = 0
            total_investment = 0
            daily_returns = []
            best_worst_year = []
            weighted_returns = 0
            for weight, ticker in zip(weights,tickers):

                if ticker in self.download_cache:
                    data = copy.deepcopy(self.download_cache[ticker])

                else:
                    with open(os.devnull, 'w') as fnull:
                        with redirect_stdout(fnull), redirect_stderr(fnull):
                            data   = yf.download(ticker, period="max")
                    self.download_cache[ticker] = copy.deepcopy(data)

                # Reformat the dataframe
                data["Date"] = pd.to_datetime(data.index)
                data["Year"] = data.Date.dt.year
                data.reset_index(drop=True, inplace=True)

                if "Adj Close" not in data.columns:
                    # Renaming a single column
                    data.rename(columns={'Close': 'Adj Close'}, inplace=True)

            #     # Reformat the dataframe
            #     data.columns = data.columns.droplevel(1)

                # Keep full years by dropping leading and trailing years
                start_end = data.groupby("Year").agg(year_start = ("Date","min"), year_end=("Date","max"))

                if trim_method == "auto":
                    start_date = start_end.index[0]
                elif isinstance(trim_method,int):
                    start_date = trim_method
                else:
                    start_date = self.earliest_date.year

                price = data[(data.Year > start_date) & (data.Year < start_end.index[-1])][["Date","Year","Adj Close",]]
                # price = data[(data.Year > 2010) & (data.Year < start_end.index[-1])][["Date","Year","Adj Close",]]

                adj_close = price["Adj Close"].values
                t_prime = price["Adj Close"].shape[0]
                t = 252 #Average days markets are open
                # append a values to make it divisable by 252.
                # This will results in zeros are the end. Zero padding
                adj_close = np.hstack([adj_close,np.full(t - len(adj_close)%t,adj_close[-1])])

                # Compute the daily_returns to get std and risk statistics
                returns = adj_close[1:]/adj_close[:-1]-1
                returns = np.hstack([returns, returns[-1::]]) # Pad with an extra 0
                daily_returns.append(returns)

                if not weight:
                    portfolio.append(0)
                    continue



                # TODO how can we add dividend?
                adj_close = adj_close.reshape(-1,t)

                # Yearly computation taking into account expense ratio
                expense = info_cache[ticker].get("expense") or info_cache[ticker].get("netExpenseRatio")/100
                purchase_price = adj_close[:,::10] #every two weeks early DCA
                number_of_years = purchase_price.shape[0]
                investment_amount = purchase_amount*weight/purchase_price.shape[1]

                quantity = investment_amount/purchase_price

                end_of_year_price = purchase_price[:,-1]
                yearly_returns = np.cumsum(np.sum(quantity,axis=1)) * end_of_year_price
                yearly_investment_total = np.sum(quantity * purchase_price, axis=1)
                yearly_investment_total[1:] = yearly_returns[:-1]
                rate = (yearly_returns/yearly_investment_total  - 1 + expense)*100
                yearly_returns_minus_expenses = yearly_investment_total*(1+rate/100-expense)

                expenses += weight*expense
                portfolio.append(np.sum(yearly_returns_minus_expenses))

                if ticker not in plotted:

                norm_price = (price["Adj Close"]-min(price["Adj Close"]))/max(price["Adj Close"])
                plt.plot(price["Date"],norm_price, label=f"{ticker}-{info_cache[ticker]["longName"]}")
                plotted.append(ticker)

                #Add portoflio historical price
                portfolio_historical_price += (price["Adj Close"] * weight)

            if 0 not in weights:
                norm_historical_price = (portfolio_historical_price-min(portfolio_historical_price))/max(portfolio_historical_price)
                plt.plot(price["Date"],norm_historical_price, label=f"{weights[0]}/{weights[1]}% stock/bond")

            total_investment = purchase_amount * number_of_years
            # Stats to compute the efficient frontier
            daily_returns = np.array(daily_returns).T

            # TODO i need to remove the zero padding using `t_prime`
            expected_return = np.mean(daily_returns,axis=0)
            std_returns = daily_returns-expected_return

            # if std_returns.shape[1]>1:
            #   covar = np.cov(std_returns.T,ddof=1)
            #   std_dev = np.std(daily_returns,axis=0,ddof=1) # Small is better
            #   current_weights = np.array(weights).reshape(1,-1)
            #   std_portfolio = np.sqrt(current_weights@covar@current_weights.T).item()
            # else:
            #   std_dev = np.std(daily_returns,axis=0,ddof=1) # Small is better
            #   std_portfolio =  covar   = std_dev**2

            weighted_returns = np.sum(daily_returns * np.array(weights),axis=1)
            bw_year = weighted_returns.reshape(t,-1)
            bw_year = np.sum(bw_year,axis=0)

            bw_month = weighted_returns.reshape(21,-1)
            bw_month = np.sum(bw_month,axis=0)
            positive_years = bw_year>0
            best_worst_year.append({"best day":float(np.max(weighted_returns)),
                                    "worst day":float(np.min(weighted_returns)),
                                    "best year":float(np.max(bw_year)),
                                    "worst month":float(np.min(bw_month)),
                                    "best month":float(np.max(bw_month)),
                                    "worst year":float(np.min(bw_year)),
                                    "up market":int(np.sum(positive_years)),
                                    "down market":int(np.sum(~positive_years))})

            # Compound Annual Growth Rate (CAGR), use the formula: CAGR = (Ending Value / Beginning Value)^(1 / Number of Years) - 1. Multiply the result by 100 to convert it to a percentage
            # Geometric Mean / CAGR (The Accurate Way)
            # The Compound Annual Growth Rate (CAGR) is the "gold standard" in finance. It tells you the actual rate at which your money grew, accounting for the fact that a 50% loss requires a 100% gain just to break even.
            equity = float(sum(portfolio))
            CAGR = np.power(equity/total_investment,1/number_of_years) *100 - 1
            portfolio_outcomes.append({"name":name,
                                        "tickers":tickers,
                                        "weights":weights,
                                        "expense":expenses,
                                        "CAGR":float(CAGR),
                                        #  "covar":covar,
                                        "std_returns":std_returns,
                                        "expected_return":expected_return,
                                        #  "std_dev":std_dev,
                                        #  "std_portfolio":float(std_portfolio),
                                        "best_worst_year":best_worst_year,
                                        "Number of Years":number_of_years,
                                        "total investment":total_investment,
                                        "equity":equity})

            plt.legend()
            plt.xlabel("Year")
            plt.ylabel("Close Value ($)")
            plt.show(block=False)