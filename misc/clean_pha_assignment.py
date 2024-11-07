# -*- coding: utf-8 -*-
"""clean_pha_assignment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e_I4USaQn-jjWOfQd_5yMHkRoq2GcNxS
"""

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

#load data

pha_data = pd.read_csv('/content/drive/MyDrive/mable/Public_Housing_Authorities_9202502862256052792.csv')

# 1.2 Calculation of Total Units
# We are using 'SECTION8_UNITS_CNT' as the total number of HPV units
# We calculate the non-HPV units total count as total_ph_units:
pha_data['total_ph_units'] = pha_data['PHA_TOTAL_UNITS']-pha_data['SECTION8_UNITS_CNT']

# 1.1: Condensed dataset creation
# I subsetted the original dataset with columns A-N (OBJECTID through HA_COMBINED_SIZE_CATEGORY) using the df.loc() method
# and then joined that subset to another subset created in the same way that includes column Y (PHA_TOTAL_UNITS) and the
# two new columns I created in part 1.2

## cols A-N (first 14 cols), col Y, total_hcv_units, total_ph_units
condensed_data = pha_data.loc[:, 'OBJECTID':'HA_COMBINED_SIZE_CATEGORY'].join(pha_data.loc[:, ['PHA_TOTAL_UNITS', 'total_ph_units']])

# I am moving the 'SECTION8_UNITS_CNT' to be next to the other total units counts for ease of reading
condensed_data = condensed_data[['OBJECTID', 'PARTICIPANT_CODE', 'FORMAL_PARTICIPANT_NAME', 'HA_PHN_NUM',
       'HA_FAX_NUM', 'HA_EMAIL_ADDR_TEXT', 'EXEC_DIR_PHONE', 'EXEC_DIR_FAX',
       'EXEC_DIR_EMAIL', 'PHAS_DESIGNATION', 'HA_LOW_RENT_SIZE_CATEGORY',
        'HA_SECTION_8_SIZE_CATEGORY',
       'HA_COMBINED_SIZE_CATEGORY', 'PHA_TOTAL_UNITS', 'SECTION8_UNITS_CNT','total_ph_units']]
# I used the following line, now commented out to double check the head and tail of the condensed dataset before
# sorting it
#print('CHECKING CONDENSED DATA PRE-SORT \n HEAD:', condensed_data.head(3), '\n TAIL \n', condensed_data.tail(3))

## sort by PHA_TOTAL_UNITS using the df.sort_values() method:
condensed_data = condensed_data.sort_values(by = 'PHA_TOTAL_UNITS')

# Use the following print command to double check the head and tail of sorted condensed data
#print('CHECKING CONDENSED DATA POST-SORT \n HEAD:', condensed_data.head(3), '\n TAIL \n', condensed_data.tail(3))

# Export condensed dataset as CSV
condensed_data.to_csv('condensed_pha_dataset.csv')

condensed_data

# Now I use Plotly Express to whip up some ECDFs...

hcv_fig = px.ecdf(condensed_data, x='SECTION8_UNITS_CNT', title = 'Empirical CDF of Total Number of HCV Units',
              labels = {'SECTION8_UNITS_CNT':'Total HCV Units (by Housing Authority)'},
              ecdfnorm = 'percent')
hcv_fig.show()
ph_fig.write_html('hcv_ecdf.html')

ph_fig = px.ecdf(condensed_data, x='total_ph_units', title = 'Empirical CDF of  Number of Non-HPV Public Housing Units',
              labels = {'total_ph_units':'Total Non-HPV Public Housing Units (by Housing Authority)'},
              ecdfnorm = 'percent')
ph_fig.show()
ph_fig.write_html('ph_ecdf.html')

ph_fig = px.ecdf(condensed_data, x='PHA_TOTAL_UNITS', title = 'Empirical CDF of Total Number of Public Housing Units',
              labels = {'PHA_TOTAL_UNITS':'Total Public Housing Units (by Housing Authority)'},
              ecdfnorm = 'percent')
ph_fig.show()
ph_fig.write_html('total_pha_units_ecdf.html')

# Final Output: Medians
print('The median number of HCV units across all housing authorities is ',round(condensed_data['SECTION8_UNITS_CNT'].median(), 5),'\n'
      'The median number of public housing units across all housing authorities is ',round(condensed_data['total_ph_units'].median(),5), '\n')

# 2.1: Formulation of Cost Calculation
# inputs: per_unit_cost, per_HCV_unit_cost, flat_cost
# other variables: Total Units (total units of each housing authority: using PHA_TOTAL_UNITS ), Total HCV Units (total_hcv_units)

class Market_Size_Analysis:

  def __init__(self, data: pd.DataFrame):
    self.data = data

  def total_cost_calc(self, per_unit_cost, per_HCV_unit_cost, flat_cost):
    self.total_cost = (self.data['PHA_TOTAL_UNITS'] * per_unit_cost) + (self.data['SECTION8_UNITS_CNT'] * per_HCV_unit_cost) + flat_cost
    self.data['total_cost'] = self.total_cost
    return self.total_cost
    # 2.1: Formulation of Cost Calculation, adding column to the dataset

  def required_price_calc(self, margin: float):
    self.required_price = self.total_cost / (1 - margin)
    self.data['required_price'] = self.required_price
    return self.required_price
    # 2.2 Price Calculation for Margin, adding column to the dataset

  def margin_calc(self, price):
    self.margin = 1 - (self.total_cost/ price)
    self.data['margin'] = self.margin
    return self.margin
    # 2.3 Margin Calculation for Given Price, adding column to the dataset

  def sam_calc(self, margin):
      self.sam = self.total_cost.sum() * margin
      print('The SAM is', self.sam)
      return self.sam
      # 2.4 Service Addressable Market (SAM) Calculation,
      # summing the costs for each PHA and multiplying by margin, returning SAM

msa = Market_Size_Analysis(condensed_data)
example_per_unit_cost = 30
example_per_HCV_unit_cost = 20
example_flat_cost = 3000
example_margin = 0.3
example_price = 11000 # example price slightly higher than median required price
msa.total_cost_calc(example_per_unit_cost,example_per_HCV_unit_cost,example_flat_cost)
msa.required_price_calc(example_margin)
msa.margin_calc(example_price)
msa.sam_calc(example_margin)

# and now export to a csv
msa.data.to_csv('market_size_analysis_dataset.csv')



# Making a little dataset with the medians:
median_dataset = {'SECTION8_UNITS_CNT': condensed_data['SECTION8_UNITS_CNT'].median(), 'PHA_TOTAL_UNITS':condensed_data['PHA_TOTAL_UNITS'].median()}

# Using the same example costs, remember the example margin is 0.3 or 30%
median_msa = Market_Size_Analysis(median_dataset) # using medians
median_msa.total_cost_calc(example_per_unit_cost, example_per_HCV_unit_cost, example_flat_cost)
median_msa.required_price_calc(example_margin)
print('$', round(median_msa.required_price, 2), 'is the median price')
# export the dataset


