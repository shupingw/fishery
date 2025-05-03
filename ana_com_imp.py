# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 23:45:45 2025

@author: ShupingWang
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### need to instal adjustText using Anaconda
### conda install -c conda-forge adjusttext

#%% Step1: define a function to add council information to a dataset only has state name
## define a clean_value function to process numeric data as string

def add_council_info(df, state_fips = None, fips_council=None):
    data = df.copy()

    state_fips_df = pd.read_csv(r'data/state_fips.csv')
    state_fips_df = state_fips_df.rename(columns={'STATEFP': 'fips', 'STATE_NAME': 'state'})
    # Create default council mapping if not provided
    fips_council = pd.read_csv(r'data/fips_council_mapping.csv')
    
    data = data.merge(
        state_fips_df[['fips', 'state']], 
        on='state',                      
        how='left'                      
    )
    
    fips_to_council = dict(zip(fips_council['fips'], fips_council['council_id']))
    council_id_to_name = dict(zip(fips_council['council_id'], fips_council['council_name']))
    
    data['council_id'] = 'Unknown'
    data['council_name'] = 'Unknown'
    
    mask = data['fips'].isin(fips_to_council.keys())
    

    data.loc[mask, 'council_id'] = data.loc[mask, 'fips'].map(fips_to_council)
    
    data.loc[mask, 'council_name'] = data.loc[mask, 'council_id'].map(council_id_to_name)
    
    return data

def clean_value(val):
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return val

## Add this code so that when I import the function from this file, the entire file won't be executed
if __name__ == "__main__":
    pass
    
    
#%% Step2: merge commercial data with licenses data

com_imp = pd.read_csv(r'data/commercial_impact_state.csv')
com_imp = com_imp.rename(columns={'State': 'state'})
com_imp_upd = add_council_info(df=com_imp)
com_imp_df = com_imp_upd[(com_imp_upd['Sector'] == 'Total Impacts') & (com_imp_upd['Imports'] == 'Without Imports')]
licenses = pd.read_csv(r'data/licenses.csv')
licenses_df = licenses[(licenses['year'] == 2022)]
licenses_df = licenses_df.drop(['state', 'council_id', 'council_name'], axis=1)

merged = com_imp_df.merge(licenses_df, on='fips', how='left')

#%% Step3: draw graph -- Jobs and licenses by state, colored by council
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_tex

# Load the data
df = merged

# Proceed with filtering based on actual data
jobs_data = df[df['Impact Type'] == '#Jobs'].copy()
value_added_data = df[df['Impact Type'] == 'Value Added'].copy()

# Clean the numeric values
jobs_data['Impact Value'] = jobs_data['Impact Value'].apply(clean_value)
value_added_data['Impact Value'] = value_added_data['Impact Value'].apply(clean_value)

# Create data for plotting
plot_data = []
# Get all unique states from the dataframe
states = df['state'].unique()

for state in states:
    # Find councils for this state
    state_councils = df[df['state'] == state]['council_name'].unique()
    if len(state_councils) == 0:
        continue
    
    council = state_councils[0]  
    
    # Find data for this state
    state_jobs = jobs_data[(jobs_data['state'] == state) & (jobs_data['Sector'] == 'Total Impacts')]    state_value = value_added_data[(value_added_data['state'] == state) & (value_added_data['Sector'] == 'Total Impacts')]
    state_value = value_added_data[(value_added_data['state'] == state) & (value_added_data['Sector'] == 'Total Impacts')]

    # Get license data for this state
    state_licenses = df[df['state'] == state]['paid_holders'].values
    if len(state_licenses) > 0:
        license_value = state_licenses[0] 
    else:
        continue
    
    if len(state_jobs) > 0 and len(state_income) > 0 and len(state_value) > 0:
        jobs_value = state_jobs['Impact Value'].values[0] 
        value_added = state_value['Impact Value'].values[0]
        
        plot_data.append({
            'state': state,
            'council_name': council,
            'licenses': license_value,
            'jobs': jobs_value,
            'value_added': value_added
        })

# Convert to DataFrame
plot_df = pd.DataFrame(plot_data)

if len(plot_df) == 0:
    print("No data to plot. Check filtering criteria.")
    exit()

# Now create the visualization
# Create a map of councils to colors
colormap = plt.cm.Set1
council_colors = {council: colormap(i % colormap.N) 
                 for i, council in enumerate(plot_df['council_name'].unique())}

# Create the plot
fig, ax = plt.subplots(figsize=(14, 10))
# Plot each state as a bubble
for i, row in plot_df.iterrows():
    # Size based on value added - adjust the scaling factor for better visibility
    size = np.sqrt(row['value_added']) / 40
    size = max(100, min(2000, size))
    
    plt.scatter(
        row['licenses'], 
        row['jobs'],  # Changed from income to jobs
        s=size,  # This size represents value_added
        color=council_colors[row['council_name']],
        alpha=0.7,
        edgecolor='black',
        linewidth=1
    )

# Define your council markers
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=20, label=council)
                 for council, color in council_colors.items()]

# Create ONLY those elements in the legend
plt.legend(handles=legend_elements, 
           title="Fishery Councils", 
           loc='upper right',
           fontsize=15,
           title_fontsize=18,
           framealpha=0.9,
           edgecolor='black',
           borderpad=1,
           labelspacing=1.2)  

# Add labels and title
plt.xlabel('Licenses', fontweight='bold', fontsize=24)
plt.ylabel('Jobs', fontweight='bold',fontsize=24)  # Changed from Income ($) to Jobs
plt.title('Fishery Economic Impact on Jobs by State, \nCommercial Sector (2022)', fontsize=28, fontweight='bold')

# Add grid lines
plt.grid(True, linestyle='--', alpha=0.7)
max_x = plot_df['licenses'].max() * 1.1  # Add 10% buffer
max_y = plot_df['jobs'].max() * 1.1  # Add 10% buffer
plt.xlim(0, max_x)
plt.ylim(0, max_y)  # Adjust this based on your jobs data range
plt.yticks(fontsize=20)
plt.xticks(fontsize=20)


# Get current axes
ax = plt.gca()

# Create a list to store all text objects
texts = []

# Add text for each point
for i, row in plot_df.iterrows():
    texts.append(plt.text(
        row['licenses'], 
        row['jobs'],
        row['state'],
        fontsize=16,
        ha='center'
    ))

# Adjust the texts to prevent overlapping
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red', alpha=0.5))


## Add the reference line as y = 0.1x
max_x_for_line = plot_df['licenses'].max() * 1.1  # Same buffer as used for xlim
x_line = np.linspace(0, max_x_for_line, 100)
y_line = 0.1 * x_line
plt.plot(x_line, y_line, color='red', linestyle='--', linewidth=2) ##label='y = 0.1x'
plt.text(max_x/2, max_y/1.2, "Jobs equals 10% licenses holders", ha='center', fontsize=20, alpha=0.7)


# Format the axes with commas for thousands
from matplotlib.ticker import FuncFormatter
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, p: '{:,}'.format(int(y))))  # Changed from currency to integer format

# Save and show
plt.tight_layout()
plt.savefig('result/fishery_state_commercial_impact_jobs.png', dpi=300)
plt.show()


