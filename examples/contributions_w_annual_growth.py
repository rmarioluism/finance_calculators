import numpy as np
import pandas as pd
from finance_calculators.calc_contributions import total_contribution, reformat, MaxContribution

# Yearly income estimates using hourly rates and 52 pay periods.
# part-time, full-time, 4 hours overtime and 8 hours overtime
hourly_rate = 75
income      = np.array([15, 20, 30, 40, 50, 60]).reshape(-1,1) * hourly_rate * 52
year = 2026

max_contritions_dict = MaxContribution(year)
max_contribution = max_contritions_dict.get("401k employee", year)

#This is an estimate. The max is 70000 - employee contribution for 2025
max_employer_contribution = max_contritions_dict.get("401k max", year) - max_contribution

# Multiple investment percentages
percentage   = np.array([ .10, .12, .13, .14, .15, .16, .17, .18]).reshape(1,-1)
match_percentage  = np.array([.01, .02, .03, .04, .05,.06,.07, .10]).reshape(1,-1)

# Employee contribution per year
amounts_df_yr = total_contribution(income,percentage,periods=1,max_contribution=max_contribution)

# Employer contribution per year
amounts_df_yr_matching = total_contribution(income,match_percentage,periods=1,max_contribution=max_employer_contribution)

# Create a dataframe that adds the two contributions using one employer matching percentage
columns = [float(c)+float(b) for b,c in zip(amounts_df_yr.columns.values[1:], amounts_df_yr_matching.columns.values[1:])]
columns = [amounts_df_yr.columns.values[0]] + columns
total_df = pd.DataFrame(amounts_df_yr.values + amounts_df_yr_matching.values,columns=columns)
total_df.Income = amounts_df_yr.Income

amounts = reformat(total_df.copy(),periods=1,contribution_type= "total")

#https://www.calculator.net/401k-calculator.html
#https://www.calculatorsoup.com/calculators/financial/future-value-annuity-calculator.php
i = 10/100 #APY
G = .01 # Annual income increase
N = 65 - 38 # Assuming retiring at 65yrs old
T = 1 #ordinary annuity. Beginning of the period
T = 0 #annuity due. End of the period

if G<=0.0:
  total_df.iloc[:,1:] *= (np.power(1+i,N)-1)*(1+i*T)/i #Not assuming annual growth
  print("Assumming no annual growth")
else:
  # https://www.calculatorsoup.com/calculators/financial/future-value-calculator.php#formulas
  #https://www.calculator.net/investment-calculator.html?ctype=endamount&ctargetamountv=1%2C000%2C000&cstartingprinciplev=0&cyearsv=10&cinterestratev=6&ccompound=monthly&ccontributeamountv=7%2C000&cadditionat1=end&ciadditionat1=annually&printit=0&x=Calculate#calresult
  # TODO update this to be compounded monthly, yearly, daily, etc...
  # This is off by a some amount when compared to the calculatorsoup result
  total_df.iloc[:,1:] *= (np.power(1+i,N)-np.power(1+G,N))*(1+i*T)/(i-G) #Assuming annual growth
  print("Assumming annual growth")

amounts_fv = reformat(total_df.copy(),periods=1,contribution_type= "total")
