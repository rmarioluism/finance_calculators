# import matplotlib as mpl

# # Use 'TkAgg' for Windows/Linux
# mpl.use('TkAgg')

import matplotlib as mpl

# Set global default font size for x and y tick labels
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['axes.labelsize'] = 20

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf

pd.options.mode.copy_on_write = True

tickers = ["SPY","VCR","VFH","VOO","VUG","MGK","VGT","VTI"]

data   = yf.download("SPY", period="max")

# Reformat the dataframe
data["Date"] = pd.to_datetime(data.index)
data["Year"] = data.Date.dt.year
data.reset_index(drop=True, inplace=True)

if "Adj Close" not in data.columns:
	# Renaming a single column
	data.rename(columns={'Close': 'Adj Close'}, inplace=True)

# Reformat the dataframe
data.columns = data.columns.droplevel(1)

# Keep full years by dropping leading and trailing years
start_end = data.groupby("Year").agg(year_start = ("Date","min"), year_end=("Date","max"))
# price = data[(data.Year > start_end.index[0]) & (data.Year < start_end.index[-1])][["Date","Year","Adj Close",]]

# plt.figure(figsize=(12,4))
# plt.plot(price["Date"],price["Adj Close"])
# plt.xlabel("Year")
# plt.ylabel("Close Value ($)")
# plt.show(block=False)

def generate_window(a, w = 4, overlap = 2, copy = False):
		#https://stackoverflow.com/questions/45730504/how-do-i-create-a-sliding-window-with-a-50-overlap-with-a-numpy-array
		sh = (a.size - w + 1, w)
		st = a.strides * 2
		view = np.lib.stride_tricks.as_strided(a, strides = st, shape = sh)[0::overlap]
		if copy:
				return view.copy()
		else:
				return view

window_years = 28
overlap_years = 1
years = generate_window(start_end.index.values[1:-1],window_years,overlap_years)

years_string = [f"{s}-{e}" for s,e in years[:,[0,-1] ]][:4]
values = []
purchase_amount = 25000
flag = 0
for start_year,end_year in years[:,[0,-1]]:
	price = data[(data.Year > start_year) & (data.Year < end_year)][["Date","Year","Adj Close",]]

	adj_close = price["Adj Close"].values
	t = 252 #Average days markets are open
	# append a values to make it divisable by 252.
	adj_close = np.hstack([adj_close,np.full(t - len(adj_close)%t,adj_close[-1])])
	adj_close = adj_close.reshape(-1,t)

	# TODO this is wrong. The portfolio comparison has the right code
	#TODO add a random location
	perfect_timing = pd.DataFrame(np.min(adj_close,axis=1),columns=['Adj Close'])
	poor_timing = pd.DataFrame(np.max(adj_close,axis=1),columns=['Adj Close'])
	idx_perfect = np.argmin(adj_close,axis=1)
	idx_poor = np.argmax(adj_close,axis=1)

	front_loading = pd.DataFrame(adj_close[:,0],columns=['Adj Close']) # Beginning of the year
	end_loading   = pd.DataFrame(adj_close[:,-1],columns=['Adj Close'])  # End of the year or unloading
	early_dca = adj_close[:,::10] #every two weeks
	# late_dca  = adj_close[:,10::10] #every two weeks

	idx_dca = np.repeat(np.arange(adj_close.shape[1])[::10],adj_close.shape[0]).reshape(-1,adj_close.shape[0])
	if flag == 0 :
		plt.figure(figsize=(16,16));plt.plot(adj_close.T);plt.xlabel("Open Market Days");plt.ylabel("Close Price")
		plt.scatter(idx_perfect, perfect_timing,color="green",marker=r'$\$$',s=1000)
		plt.scatter(idx_poor, poor_timing,color="red",marker=r'$\$$',s=1000)
		plt.scatter(idx_dca, early_dca.T,color="k",marker=r'$\$$',s=200)
		plt.ylim([195, 360])
		plt.title(f"SPY-500 One Year Windows", fontsize=20)
		plt.show(block=False)
		flag +=1

	
	early_dca = pd.DataFrame(early_dca.reshape(-1,1),columns=['Adj Close'])
	# total_cost = early.shape[0]*purchase_amount
	current_price   = price.iloc[-1]['Adj Close']

	two_weeks = purchase_amount/(52/2)
	lump_sum = purchase_amount #TODO this is assuming a fix purchase price.

	temp = []
	for df,investment_amount in zip([perfect_timing,front_loading, early_dca, end_loading,poor_timing],
								  [lump_sum,lump_sum,two_weeks, lump_sum,lump_sum]):
		
		df.loc[:, ('Quantity')]     = np.round(investment_amount/df.loc[:,('Adj Close')],2) # (Investment amount in Dollars)/(stock price)
		df.loc[:, ("Market Value")] = df["Quantity"] * current_price # Current market values of each purchase
		temp.append(df["Market Value"].sum())
	values.append(temp)

values = np.array(values)

colors = ['#F8A205', '#7C241B', '#114155', '#3B97B6',"#2A9D8F","#E76F51"]

# print(values)
years = np.array([ 10, 20, 30, 40])
try:
	width = (years[1]-years[0])/5
except:
	width = 1/5


# values = [np.array(values) , np.array(values) - contribution*years]
values = [values , (values.T - np.max(values,axis=1)).T]

width = 1.5 # Increased width to be proportional to the increased spacing
fig,axes = plt.subplots(1,2,figsize=(8*2,6))
axes = axes.ravel()
titles = ["Investment Strategies Returns","Comparing Strategy Difference"]
labels = ["Perfect Timing", "Front Loading", "Dollar Cost Average","Unloading","Poor Timing"]

for ax,title, present_value, year in zip(axes,titles, values, years):
	
	# Sort the 

	ax.bar(years - width*2, present_value[:4,0], width=width, color='#F8A205', align='center', label=labels[0])
	ax.bar(years - width,   present_value[:4,1], width=width, color='#114155', align='center', label=labels[1])
	ax.bar(years ,   present_value[:4,2], width=width, color='#7C241B', align='center', label=labels[2])
	ax.bar(years + width, present_value[:4,3], width=width, color='#427E7F', align='center', label=labels[3])
	ax.bar(years + width*2, present_value[:4,4], width=width, color='#606060', align='center', label=labels[4])
	ax.legend(fontsize=20)
	ax.set_title(title,fontsize=20)
	ax.set_xlabel("Years of Investments")
	ax.set_ylabel("Portfolio Balance ($)")
	ax.set_xticks(years, years_string)

print(purchase_amount)
plt.show()
print("DOne")








































# TODO implement this using a for loop and using varying growth and returns


contribution = 7000
years = np.array([10, 20, 30, 40])
T = 1
r = 10
i = r/100
early = contribution*(np.power(1+i,years)-1)*(1+i*T)/i #Not assuming annual growth

T = 0
i = r/100
late = contribution*(np.power(1+i,years)-1)*(1+i*T)/i #Not assuming annual growth Eq 2.2

# Compounding
T = 1 #Early
m = 12
i = r/(m*100)
dca = contribution/m*(np.power(1+i,years*m)-1)*(1+i*T)/i #Not assuming annual growth

T = 0
i = r/(m*100)
late_dca = contribution/m*(np.power(1+i,years*m)-1)*(1+i*T)/i

values = [early, dca, late_dca, late]

try:
	width = (years[1]-years[0])/5
except:
	width = 1/5

fig,axes = plt.subplots(1,2,figsize=(8*2,6))
axes = axes.ravel()
# values = [np.array(values) , np.array(values) - contribution*years]
values = [np.array(values) , np.array(values) - np.max(values,axis=0)]


for ax, present_value, year in zip(axes,values, years):
	ax.bar(years - width*3/2, present_value[0,:], width=width, color='#F8A205', align='center', label="Early")
	ax.bar(years - width/2,   present_value[1,:], width=width, color='#114155', align='center', label="Early Dollar Cost Average")
	ax.bar(years + width/2,   present_value[2,:], width=width, color='#7C241B', align='center', label="Late Dollar Cost Average")
	ax.bar(years + width*3/2, present_value[3,:], width=width, color='#3B97B6', align='center', label="Late")
	ax.legend()
	ax.set_xlabel("Years of Investments")
	ax.set_ylabel("Gained Interest")
	ax.set_xticks(years, years)

plt.show()


PV = 15000
t = 10
r = 1.5/100
m = 12
g = 0
PMT = 100
q = 12
T = 0
FV = PV * np.power(1+r/m, m*t) + PMT/(r/m) * (np.power(1+r/m,m*t)-1)*(1+(r/m)*T)