# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 23:45:45 2025

@author: ShupingWang
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
!pip install adjustText
#%%

def add_council_info(df, state_fips = None, fips_council=None):
    """
    Add council ID and council name information to licenses dataframe.
    
    Parameters:
    -----------
    licenses_df : pandas.DataFrame
        The dataframe containing license information with a 'state' column
    state_fips_df : pandas.DataFrame, optional
        The dataframe with state to FIPS code mapping (must have 'fips' and 'state' columns)
        If None, a default mapping will be created
    council_mapping_df : pandas.DataFrame, optional
        The dataframe with FIPS to council mapping (must have 'fips', 'council_id', and 'council_name' columns)
        If None, a default mapping will be created
    
    Returns:
    --------
    pandas.DataFrame
        The licenses dataframe with added 'council_id' and 'council_name' columns
    """
    
    # Create a copy to avoid modifying the original dataframe
    data = df.copy()
    

    state_fips_df = pd.read_csv(r'data/state_fips.csv')
    state_fips_df = state_fips_df.rename(columns={'STATEFP': 'fips', 'STATE_NAME': 'state'})
    # Create default council mapping if not provided
    fips_council = pd.read_csv(r'data/fips_council_mapping.csv')
    
    # Step 1: Merge licenses with state_fips to get FIPS codes
    data = data.merge(
        state_fips_df[['fips', 'state']], 
        on='state',                      
        how='left'                      
    )
    
    # Step 2: Create mapping dictionaries from council_mapping_df
    fips_to_council = dict(zip(fips_council['fips'], fips_council['council_id']))
    council_id_to_name = dict(zip(fips_council['council_id'], fips_council['council_name']))
    
    # Step 3: Initialize council columns with 'Unknown'
    data['council_id'] = 'Unknown'
    data['council_name'] = 'Unknown'
    
    # Step 4: Use vectorized operations instead of iterating through rows
    # Filter rows where FIPS is in our mapping dictionary
    mask = data['fips'].isin(fips_to_council.keys())
    
    # Update council_id for matching rows
    data.loc[mask, 'council_id'] = data.loc[mask, 'fips'].map(fips_to_council)
    
    # Update council_name based on council_id
    data.loc[mask, 'council_name'] = data.loc[mask, 'council_id'].map(council_id_to_name)
    
    return data

## Section 2. draw graph
com_imp = pd.read_csv(r'data/commercial_impact_state.csv')
com_imp = com_imp.rename(columns={'State': 'state'})
com_imp_upd = add_council_info(df=com_imp)
com_imp_df = com_imp_upd[(com_imp_upd['Sector'] == 'Total Impacts') & (com_imp_upd['Imports'] == 'Without Imports')]
licenses = pd.read_csv(r'data/licenses.csv')
licenses_df = licenses[(licenses['year'] == 2022)]
licenses_df = licenses_df.drop(['state', 'council_id', 'council_name'], axis=1)

merged = com_imp_df.merge(licenses_df, on='fips', how='left')

#%% Jobs and Incomes == perfect linear, not interesting
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = merged
# Clean the data
def clean_value(val):
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return val

# Proceed with filtering based on actual data
jobs_data = df[df['Impact Type'] == '#Jobs'].copy()
income_data = df[df['Impact Type'] == 'Income'].copy()
value_added_data = df[df['Impact Type'] == 'Value Added'].copy()
licenses_data = df['paid_holders'].copy()


# Clean the numeric values
jobs_data['Impact Value'] = jobs_data['Impact Value'].apply(clean_value)
income_data['Impact Value'] = income_data['Impact Value'].apply(clean_value)
value_added_data['Impact Value'] = value_added_data['Impact Value'].apply(clean_value)

# Create data for plotting
plot_data = []
for state in df['state'].unique():
    # Find councils for this state
    state_councils = df[df['state'] == state]['council_name'].unique()
    if len(state_councils) == 0:
        continue
    
    council = state_councils[0]  # Use first council if multiple
    
    # Find data for this state
    state_jobs = jobs_data[(jobs_data['state'] == state) & (jobs_data['Sector'] == 'Total Impacts')]
    state_income = income_data[(income_data['state'] == state) & (income_data['Sector'] == 'Total Impacts')]
    state_value = value_added_data[(value_added_data['state'] == state) & (value_added_data['Sector'] == 'Total Impacts')]
    
    if len(state_jobs) > 0 and len(state_income) > 0 and len(state_value) > 0:
        job_value = state_jobs['Impact Value'].values[0]
        income_value = state_income['Impact Value'].values[0]
        value_added = state_value['Impact Value'].values[0]
        
        plot_data.append({
            'state': state,
            'council_name': council,
            'jobs': job_value,
            'income': income_value,
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
plt.figure(figsize=(14, 10))

# Plot each state as a bubble
for i, row in plot_df.iterrows():
    # Size based on value added - adjust the scaling factor for better visibility
    size = np.sqrt(row['value_added']) / 50  # Modified scaling factor
    size = max(100, min(2000, size))  # Increased minimum size for better visibility
    
    plt.scatter(
        row['jobs'], 
        row['income'],
        s=size,  # This is where size is applied based on value_added
        color=council_colors[row['council_name']],
        alpha=0.7,
        edgecolor='black',
        linewidth=1
    )

# Create a legend for the councils
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                              markerfacecolor=color, markersize=10, label=council)
                  for council, color in council_colors.items()]
plt.legend(handles=legend_elements, title="Fishery Councils", loc='upper left')

# Add labels and title
plt.xlabel('Jobs', fontweight='bold')
plt.ylabel('Income ($)', fontweight='bold')
plt.title('Fishery Economic Impact by State (2022)', fontsize=16, fontweight='bold')

# Add grid lines
plt.grid(True, linestyle='--', alpha=0.7)

# Set the axis limits as specified
plt.xlim(0, 100000)
plt.ylim(0, 2500000000)  # 750 million

# Add quadrant lines based on median values
x_mid = 50000  # midpoint of x-axis
y_mid = 1250000000  # midpoint of y-axis
plt.axvline(x=x_mid, color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=y_mid, color='gray', linestyle='--', alpha=0.5)

# Annotate quadrants (optional)
plt.text(x_mid/2, y_mid*1.75, "High Income\nLow Jobs", ha='center', fontsize=10, alpha=0.7)
plt.text(x_mid*1.75, y_mid*1.75, "High Income\nHigh Jobs", ha='center', fontsize=10, alpha=0.7)
plt.text(x_mid/2, y_mid*0.25, "Low Income\nLow Jobs", ha='center', fontsize=10, alpha=0.7)
plt.text(x_mid*1.75, y_mid*0.25, "Low Income\nHigh Jobs", ha='center', fontsize=10, alpha=0.7)

# Format the axes with commas for thousands
from matplotlib.ticker import FuncFormatter
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, p: '${:,.0f}M'.format(y/1000000)))

# Save and show
plt.tight_layout()
plt.savefig('result/fishery_state_impact.png', dpi=300)
plt.show()

#%% Income and licenses
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = merged

# Clean the data
def clean_value(val):
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return val

# Proceed with filtering based on actual data
jobs_data = df[df['Impact Type'] == '#Jobs'].copy()
income_data = df[df['Impact Type'] == 'Income'].copy()
value_added_data = df[df['Impact Type'] == 'Value Added'].copy()

# Clean the numeric values
jobs_data['Impact Value'] = jobs_data['Impact Value'].apply(clean_value)
income_data['Impact Value'] = income_data['Impact Value'].apply(clean_value)
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
    
    council = state_councils[0]  # Use first council if multiple
    
    # Find data for this state
    state_jobs = jobs_data[(jobs_data['state'] == state) & (jobs_data['Sector'] == 'Total Impacts')]
    state_income = income_data[(income_data['state'] == state) & (income_data['Sector'] == 'Total Impacts')]
    state_value = value_added_data[(value_added_data['state'] == state) & (value_added_data['Sector'] == 'Total Impacts')]
    
    # Get license data for this state
    state_licenses = df[df['state'] == state]['paid_holders'].values
    if len(state_licenses) > 0:
        license_value = state_licenses[0]  # Use the first value
    else:
        continue
    
    if len(state_jobs) > 0 and len(state_income) > 0 and len(state_value) > 0:
        income_value = state_income['Impact Value'].values[0]
        value_added = state_value['Impact Value'].values[0]
        
        plot_data.append({
            'state': state,
            'council_name': council,
            'licenses': license_value,
            'income': income_value,
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
plt.figure(figsize=(14, 10))

# Plot each state as a bubble
for i, row in plot_df.iterrows():
    # Size based on value added - adjust the scaling factor for better visibility
    size = np.sqrt(row['value_added']) / 50
    size = max(100, min(2000, size))
    
    plt.scatter(
        row['licenses'], 
        row['income'],
        s=size,  # This size represents value_added
        color=council_colors[row['council_name']],
        alpha=0.7,
        edgecolor='black',
        linewidth=1
    )

# Create a legend for the councils
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor=color, markersize=10, label=council)
                 for council, color in council_colors.items()]
plt.legend(handles=legend_elements, title="Fishery Councils", loc='upper right')

# Add labels and title
plt.xlabel('Licenses', fontweight='bold')
plt.ylabel('Income ($)', fontweight='bold')
plt.title('Fishery Economic Impact by State (2022)', fontsize=16, fontweight='bold')

# Add grid lines
plt.grid(True, linestyle='--', alpha=0.7)

# Calculate the midpoints for the x-axis based on the data
#x_mid = plot_df['licenses'].median()
#y_mid = 500000000

# Set the axis limits - for x-axis, use the range of the license data

plt.xlim(0, 2500000)
plt.ylim(0, 2500000000)  # 750 million as specified

# Add quadrant lines based on median values
plt.axvline(x=x_mid, color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=y_mid, color='gray', linestyle='--', alpha=0.5)

# Annotate quadrants
#plt.text(x_mid/2, y_mid*1.75, "High Income\nLow Licenses", ha='center', fontsize=10, alpha=0.7)
#plt.text(x_mid*1.5, y_mid*1.75, "High Income\nHigh Licenses", ha='center', fontsize=10, alpha=0.7)
#plt.text(x_mid/2, y_mid*0.25, "Low Income\nLow Licenses", ha='center', fontsize=10, alpha=0.7)
#plt.text(x_mid*1.5, y_mid*0.25, "Low Income\nHigh Licenses", ha='center', fontsize=10, alpha=0.7)

# Format the axes with commas for thousands
from matplotlib.ticker import FuncFormatter
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, p: '${:,.0f}M'.format(y/1000000)))

# Save and show
plt.tight_layout()
plt.savefig('result/fishery_state_impactq.png', dpi=300)
plt.show()


#%% Jobs and licenses
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = merged

# Clean the data
def clean_value(val):
    if isinstance(val, str):
        return float(val.replace(',', ''))
    return val

# Proceed with filtering based on actual data
jobs_data = df[df['Impact Type'] == '#Jobs'].copy()
income_data = df[df['Impact Type'] == 'Income'].copy()
value_added_data = df[df['Impact Type'] == 'Value Added'].copy()

# Clean the numeric values
jobs_data['Impact Value'] = jobs_data['Impact Value'].apply(clean_value)
income_data['Impact Value'] = income_data['Impact Value'].apply(clean_value)
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
    
    council = state_councils[0]  # Use first council if multiple
    
    # Find data for this state
    state_jobs = jobs_data[(jobs_data['state'] == state) & (jobs_data['Sector'] == 'Total Impacts')]
    state_income = income_data[(income_data['state'] == state) & (income_data['Sector'] == 'Total Impacts')]
    state_value = value_added_data[(value_added_data['state'] == state) & (value_added_data['Sector'] == 'Total Impacts')]
    
    # Get license data for this state
    state_licenses = df[df['state'] == state]['paid_holders'].values
    if len(state_licenses) > 0:
        license_value = state_licenses[0]  # Use the first value
    else:
        continue
    
    if len(state_jobs) > 0 and len(state_income) > 0 and len(state_value) > 0:
        jobs_value = state_jobs['Impact Value'].values[0]  # Get jobs value instead of income
        value_added = state_value['Impact Value'].values[0]
        
        plot_data.append({
            'state': state,
            'council_name': council,
            'licenses': license_value,
            'jobs': jobs_value,  # Changed from income to jobs
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
           labelspacing=1.2)     # Increase spacing between legend items

# Add labels and title
plt.xlabel('Licenses', fontweight='bold', fontsize=24)
plt.ylabel('Jobs', fontweight='bold',fontsize=24)  # Changed from Income ($) to Jobs
plt.title('Fishery Economic Impact on Jobs by State, \nCommercial Sector (2022)', fontsize=28, fontweight='bold')

# Add grid lines
plt.grid(True, linestyle='--', alpha=0.7)
max_x = plot_df['licenses'].max() * 1.1  # Add 10% buffer
max_y = plot_df['jobs'].max() * 1.1  # Add 10% buffer
# Since y axis is now jobs instead of income, we may need to adjust the y-axis limits
plt.xlim(0, max_x)
plt.ylim(0, max_y)  # Adjust this based on your jobs data range

plt.yticks(fontsize=20)
plt.xticks(fontsize=20)


# After creating your scatter plot but before plt.show()
import matplotlib.pyplot as plt
from adjustText import adjust_text
import numpy as np
import pandas as pd
from adjustText import adjust_text

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
plt.savefig('result/fishery_state_impact_jobs.png', dpi=300)
plt.show()


#%%

