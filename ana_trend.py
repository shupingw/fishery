# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:56:48 2025

@author: ShupingWang
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#%%
## Secion 1. Visualize trend by landings data
data = pd.read_csv(r'data/landings.csv')

landings = data.copy()
landings = landings[landings['council_id'] != 9]

plt.rcParams['figure.dpi'] = 300

# Create a pivot table to organize data by year and region
# Assuming your region column is called 'region name'
pivot_df = landings.pivot_table(
    values='dollars',
    index='year',
    columns='council_name',
    aggfunc='sum'
)

# Plot the line graph
ax = pivot_df.plot(
    kind='line',
    marker='o',
    markersize=4,
    linewidth=2,
    ax=plt.gca()
)

# Customize the plot
plt.title('Total Landing Value by Council (1950-2020)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Dollars ($)', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Council Name', loc='best', fontsize = 8)
plt.axvline(x=1976, color='gray', linestyle='--')
plt.axvline(x=1996, color='gray', linestyle='--')
plt.axvline(x=2007, color='gray', linestyle='--')

plt.text(1976, 1500000000, "Fishery Conservation \nand Management Act \nof 1976 ", ha='center', fontsize=8, alpha=0.7)
plt.text(1996, 1800000000, "Sustainable Fisheries \nAct of 1996 ", ha='center', fontsize=8, alpha=0.7)
plt.text(2011, 2200000000, "Magnuson-Stevens \nReauthorization Act of 2007", ha='center', fontsize=8, alpha=0.7)

plt.xlim(1940, 2025)
plt.ylim(0, 2500000000) 

# Format y-axis to show dollar values in millions/thousands
from matplotlib.ticker import FuncFormatter

def millions(x, pos):
    return f'${x/1000000:.1f}M' if x >= 1000000 else f'${x/1000:.0f}K'

ax.yaxis.set_major_formatter(FuncFormatter(millions))

# Add grid lines for better readability
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('result/landingvalue_by_year.png', dpi=300)
plt.show()


#%%
## Step 2. Draw data by licenses
data = pd.read_csv('data/licenses.csv')

licenses = data.copy()
licenses = licenses[licenses['council_id'] != 0]

plt.rcParams['figure.dpi'] = 300

# Create a pivot table to organize data by year and region
pivot_df = licenses.pivot_table(
    values='paid_holders',
    index='year',
    columns='council_name',
    aggfunc='sum'
)

# Create a figure with specific size to accommodate the legend
plt.figure(figsize=(12, 8))  # Increase height for more space

# Plot the line graph
ax = pivot_df.plot(
    kind='line',
    marker='o',
    markersize=4,
    linewidth=2
)

# Customize the plot
plt.title('Total Paid License Holders by Council (1960-2020)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number', fontsize=12)
plt.xticks(rotation=45)

plt.axvline(x=1976, color='gray', linestyle='--')
plt.axvline(x=1996, color='gray', linestyle='--')
plt.axvline(x=2007, color='gray', linestyle='--')


plt.text(1976, 4500000, "Fishery Conservation \nand Management Act \nof 1976 ", ha='center', fontsize=8, alpha=0.7)
plt.text(1996, 5500000, "Sustainable Fisheries \nAct of 1996 ", ha='center', fontsize=8, alpha=0.7)
plt.text(2012, 7000000, "Magnuson-Stevens \nReauthorization Act of 2007", ha='center', fontsize=8, alpha=0.7)

plt.xlim(1950, 2025)
plt.ylim(0, 8000000) 
# IMPORTANT: Adjust these values to fix the overlap
plt.subplots_adjust(bottom=0.4)  # Increase this value (0.32 → 0.35)

# Move the legend further down
plt.legend(title='Council Name', loc='lower center', bbox_to_anchor=(0.5, -0.86), ncol=3)
# Increase the negative value (-0.2 → -0.32) to move legend down

# Format y-axis to show dollar values in millions/thousands
from matplotlib.ticker import FuncFormatter
def millions(x, pos):
    return f'${x/1000000:.1f}M' if x >= 1000000 else f'${x/1000:.0f}K'
ax.yaxis.set_major_formatter(FuncFormatter(millions))

# Add grid lines for better readability
plt.grid(True, alpha=0.3)

# IMPORTANT: Remove tight_layout() as it can override your manual adjustments
plt.tight_layout()  # Comment this out

plt.savefig('result/licenseholder_by_year.png', dpi=300)
plt.show()



#%%
## Section 3. Plot of


