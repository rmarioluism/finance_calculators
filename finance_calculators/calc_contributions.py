# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# https://github.com/shahadot786/Python-Books/blob/master/Python-for-Data-Analysis.pdf
# https://github.com/codevski/python/tree/master
# https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html#sphx-glr-gallery-lines-bars-and-markers-multicolored-line-py

import numpy as np
import pandas as pd

class MaxContribution():
  max_per_year = {2026: {"401k max":72000,"401k employee":24500, "401k employee catch up":32500,"401k employee super catch up":35750,"ira":7500, "ira catch up":8600},
                  2025: {"401k max":70000,"401k employee":23500, "401k employee catch up":31000,"401k employee super catch up":34750,"ira":7000, "ira catch up":8000},}

  def __init__(self, year):
    self.year = year

  def get(self,name,year):

    if year not in self.max_per_year:
      raise ValueError(f"Data for {year} is not available. Data available for {self.max_per_year.keys()}")

    contributions = self.max_per_year[year]

    if name not in contributions:
      raise ValueError(f"Data for {name} is not available. Data available for {contributions.keys()}")

    return contributions[name]

class ColorCode:
  def __init__(self,maximum):
    self.max = maximum

  def _color_red_or_green(self, val):
    if isinstance(val,str):
      color = 'red' if float(val.replace(",","")) >= self.max else 'white'
    else:
      color = 'red' if float(val) >= self.max else 'white'

    return 'color: %s' % color

def convert2usb(x):
  """https://stackoverflow.com/questions/35019156/pandas-format-column-as-currency"""
  return "{:0,.2f}".format(float(x))

def total_contribution(income,percentage:np.ndarray,periods:np.ndarray,max_contribution:int, language = "english"):
  """
  periods: 1 for annual, 12 for monthly, 26 for biweekly, 52 for weekly
  """
  if language.lower() == "english":
    index = "Income"
  else:
    index = "Ingreso"

  # Brute Annual Income
  yearly  = income*percentage/periods

  #Contribution Cap
  yearly[yearly*periods>max_contribution] = max_contribution/periods

  amounts = np.hstack([income, yearly])
  columns = [index, *(np.round(percentage*100,2)).squeeze().tolist()]
  amounts = pd.DataFrame(amounts,columns=columns)
  return amounts

def reformat(amounts, periods=1, contribution_type= "employee", language="english",year=2026,flag_max=True, title=None):

  if language.lower() == "english":
    timeframe = {1:"Annual",12:"Monthly",26:"Biweekly",52:"Weekly"}
    index = "Income"
  else:
    timeframe = {1:"Anual",12:"Mensual",26:"Bi-Semanal",52:"Semanal"}
    index = "Ingreso"

  amounts = amounts.apply(lambda series: series.apply(convert2usb))
  amounts.set_index(index, inplace=True)

  max_contritions = MaxContribution(year)

  if contribution_type == "employee":
    caption = f"{timeframe[periods]} Contributions"
    emp_max = max_contritions.get("401k employee", year)
    map_color = ColorCode(emp_max//periods)
  elif contribution_type == "total":
    caption = f"{timeframe[periods]} Total Contributions"
    emp_max = max_contritions.get("401k max", year)
    map_color = ColorCode(emp_max//periods)
  elif contribution_type == "employer":
    caption = f"{timeframe[periods]} Employer Contributions"
    emp_max = max_contritions.get("401k max", year) - max_contritions.get("401k employee", year)
    map_color = ColorCode(emp_max//periods)
  else:
    caption = "Long Term Retirement Estimate"

  if title:
    # Overwrite the caption
    caption = title

  table_style = [{
      'selector': 'caption',
      'props': [
          # ('color', 'blue'),
          ('font-size', '32px')
      ]}]
  
  if flag_max:
    amounts = amounts.style.map(map_color._color_red_or_green).set_caption(caption).set_table_styles(table_style)
  else:
    amounts = amounts.style.set_caption(caption).set_table_styles(table_style)

  return amounts