import numpy as np
import pandas as pd
from finance_calculators.calc_contributions import total_contribution, reformat, MaxContribution

# Yearly income estimates using hourly rates and 52 pay periods.
# part-time, full-time, 4 hours overtime and 8 hours overtime
hourly_rate = 75
income      = np.array([15, 20, 30, 40, 50, 60]).reshape(-1,1) * hourly_rate * 52
year = 2025

max_contritions_dict = MaxContribution(year)

#Max for 2025

max_contribution = max_contritions_dict.get("401k employee", year)

#This is an estimate. The max is 70000 - employee contribution for 2025
max_employer_contribution = max_contritions_dict.get("401k max", year) - max_contribution

# Multiple investment percentages
percentage   = np.array([ .10, .12, .13, .14, .15, .16, .17, .18]).reshape(1,-1)
match_percentage  = np.array([.01, .02, .03, .04, .05,.06,.07, .10]).reshape(1,-1)

# Employee contribution per month
amounts_df = total_contribution(income,percentage,periods=12,max_contribution=max_contribution)
amounts = reformat(amounts_df.copy(),periods=12,contribution_type= "employee")

# Employee contribution per year
amounts_df_yr = total_contribution(income,percentage,periods=1,max_contribution=max_contribution)
amounts = reformat(amounts_df_yr.copy(),periods=1, contribution_type= "employee")

# Employer contribution per year
amounts_df_yr_m = total_contribution(income,match_percentage,periods=1,max_contribution=max_employer_contribution)
amounts = reformat(amounts_df_yr_m.copy(),periods=1,contribution_type= False)

# Create a dataframe that adds the two contributions using one employer matching percentage
total_df = pd.DataFrame(amounts_df_yr.values + amounts_df_yr_m.values,columns=amounts_df_yr.columns)
total_df.Income = amounts_df_yr.Income
columns = [float(c)+float(b) for b,c in zip(amounts_df_yr.columns.values[1:], amounts_df_yr_m.columns.values[1:])]
total_df.columns = [amounts_df_yr.columns.values[0]] + columns
amounts = reformat(total_df.copy(),periods=1,contribution_type= "total")
