import numpy as np
import matplotlib.pyplot as plt

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