# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:59:48 2025

@author: ShupingWang
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#%%
pop = pd.read_excel('data/state_population_estimates.xlsx')
pop = pop.drop(['State', 'Month'], axis=1)
pop = pop.rename(columns={'FIPS': 'fips'})

state_fips = pd.read_csv('data/national_state2020.txt', sep='|')   

state_fips = state_fips.rename(columns = {'STATEFP': 'fips', 'STATE_NAME':'state'})

pop = pop.merge(
    state_fips[['fips', 'state']], 
    on='fips',                      
    how='left'                      
)


## change dataset from wide to long
pop_indexed = pop.set_index(['state', 'fips'])

# Stack the data
pop_long = pop_indexed.stack().reset_index()

# Rename columns
pop_long.columns = ['state', 'fips', 'year', 'pop']


pop_long.to_csv('pop7017.csv', index=False)


#%%

# First, group by year to get the total US population for each year
yearly_totals = pop_long.groupby('year')['pop'].sum().reset_index()

plt.figure(figsize=(14, 6))

# Calculate growth rates on the aggregated yearly data
yearly_totals['growth_rate'] = yearly_totals['pop'].pct_change() * 100

# Plot growth rates starting from the second data point (since first has no growth rate)
plt.plot(yearly_totals['year'][1:], yearly_totals['growth_rate'][1:], 
         marker='o', linewidth=2, color='green')

plt.title('Annual U.S. Population Growth Rate (1970-2020)', fontsize=18)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Growth Rate (%)', fontsize=14)
plt.xticks(yearly_totals['year'][1:][::5], rotation=45)  # Show every 5th year
plt.grid(True, linestyle='--', alpha=0.7)

# Highlight periods of faster/slower growth
avg_growth = yearly_totals['growth_rate'][1:].mean()
plt.axhline(y=avg_growth, color='r', linestyle='--', alpha=0.7, 
            label=f'Average Growth: {avg_growth:.2f}%')

plt.legend(fontsize=12)
plt.tight_layout()
plt.show()


