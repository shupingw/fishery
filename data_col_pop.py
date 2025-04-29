# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:59:39 2025

@author: ShupingWang
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#%%
pop_7099 = pd.read_csv('pop7099s.csv')
pop_0010 = pd.read_csv('pop0010s.csv')
pop_1020 = pd.read_excel('pop1020s.xlsx')
state_fips = pd.read_csv('national_state2020.txt', sep='|')   


## for 70-99
pop_7099 = pop_7099[['fips', 'year', 'pop']]

state_fips = state_fips.rename(columns = {'STATEFP': 'fips', 'STATE_NAME':'state'})
pop_7099 = pop_7099.groupby(['year', 'fips'])['pop'].sum().reset_index()

pop_7099 = pop_7099.merge(
    state_fips[['fips', 'state']], 
    on='fips',                      
    how='left'                      
)


## for00-10
pop_0010 = pop_0010[(pop_0010['SEX'] == 0) & (pop_0010['AGE'] == 999) & (pop_0010['STATE'] != 0)]

pop_0010 = pop_0010.drop(['REGION', 'DIVISION', 'SEX', 'AGE', 'ESTIMATESBASE2000', 'CENSUS2010POP'], axis=1)

variable_list = {
    'STATE': 'fips',
    'NAME': 'state',
    'POPESTIMATE2000': 2000,
    'POPESTIMATE2001': 2001,
    'POPESTIMATE2002': 2002,
    'POPESTIMATE2003': 2003,
    'POPESTIMATE2004': 2004,
    'POPESTIMATE2005': 2005,
    'POPESTIMATE2006': 2006,
    'POPESTIMATE2007': 2007,
    'POPESTIMATE2008': 2008,
    'POPESTIMATE2009': 2009,
    'POPESTIMATE2010': 2010
    }

pop_0010 = pop_0010.rename(columns = variable_list)

## change dataset from wide to long
pop_indexed = pop_0010.set_index(['state', 'fips'])

# Stack the data
pop_0010_long = pop_indexed.stack().reset_index()

# Rename columns
pop_0010_long.columns = ['state', 'fips', 'year', 'pop']



#%%
## for11-20
pop_1120 = pop_1020[(pop_1020['year'] != 2010)]


pop_1120 = pop_1020.merge(
    state_fips[['fips', 'state']], 
    on='state',                      
    how='left'                      
)



## Combine three dataset together
combined_df = pd.concat([pop_7099, pop_0010_long, pop_1120], ignore_index=True)

# Check the result
print(f"Combined DataFrame has {len(combined_df)} rows and covers years {combined_df['year'].min()} to {combined_df['year'].max()}")



#%%
### plot 3

# First, group by year to get the total US population for each year
yearly_totals = combined_df.groupby('year')['pop'].sum().reset_index()

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



#%%
## plot 2

plt.figure(figsize=(14, 8))

# Find the top 5 states by population in the most recent year
latest_year = combined_df['year'].max()
top_states = combined_df[combined_df['year'] == latest_year].nlargest(5, 'pop')['state'].unique()

# Create line plots for each top state
for state in top_states:
    state_data = combined_df[combined_df['state'] == state]
    plt.plot(state_data['year'], state_data['pop'], marker='o', linewidth=2, label=state)

plt.title('Population Growth for Top 5 Most Populous States (1970-2020)', fontsize=18)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Population', fontsize=14)
plt.xticks(state_data['year'][::5], rotation=45)  # Show every 5th year
plt.grid(True, linestyle='--', alpha=0.7)

# Format y-axis to show numbers in millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'{x/1000000:.1f}M'))

# Add legend
plt.legend(fontsize=12)

# Show the plot
plt.tight_layout()
plt.show()