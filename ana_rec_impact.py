# -*- coding: utf-8 -*-
"""
Created on Fri May  2 21:08:56 2025

@author: ShupingWang
"""

#%%
import pandas as pd
from ana_com_imp import clean_value
from ana_com_imp import add_council_info


#%% Step1: Clean the data: combine the West Florida with West Florida across all impact types
rec_imp = pd.read_csv('data/recreational_impact_state.csv')
print("\nValue counts of Area before transformation:")
print(rec_imp['State'].value_counts())


rec_imp['Impact Value'] = rec_imp['Impact Value'].apply(clean_value)
rec_imp_com = rec_imp.copy()
# Create a copy of the dataframe
rec_imp_com = rec_imp.copy()

florida_regions = ["East Florida", "West Florida"]
florida_mask = rec_imp_com['State'].isin(florida_regions)
rec_imp_com.loc[florida_mask, 'State'] = 'Florida'
numeric_columns = rec_imp_com.select_dtypes(include=['int64', 'float64']).columns.tolist()
grouping_columns = ['State', 'Year', 'Sector', 'Impact Type']

# Remove grouping columns from numeric columns if they exist
numeric_columns = [col for col in numeric_columns if col not in grouping_columns]

# Create aggregation dictionary
agg_dict = {}
for col in numeric_columns:
    agg_dict[col] = 'sum'

# Add non-numeric columns that should take the first value
for col in rec_imp_com.columns:
    if col not in grouping_columns and col not in numeric_columns:
        agg_dict[col] = 'first'

# Group by Area, year, key species, and Hr and aggregate
rec_imp_com = rec_imp_com.groupby(grouping_columns).agg(agg_dict).reset_index()

print("Original shape:", rec_imp.shape)
print("After combining Florida regions:", rec_imp_com.shape)
print("\nValue counts of Area after transformation:")
print(rec_imp_com['State'].value_counts())

#%% Step2: Add council information and merge with licenses data
rec_imp_com = rec_imp_com.rename(columns={'State': 'state'}) 
state_summary = rec_imp_com.groupby(['state', 'Impact Type']).agg({
    'Impact Value': 'sum'
})

state_summary = state_summary.reset_index()

state_summary_upd = add_council_info(df=state_summary)

licenses = pd.read_csv(r'data/licenses.csv')
licenses_df = licenses[(licenses['year'] == 2022)]
licenses_df = licenses_df.drop(['state', 'council_id', 'council_name'], axis=1)

merged = state_summary_upd.merge(licenses_df, on='fips', how='left')


#%% Step3: creat graphs -- Jobs and licenses by state, colored by council

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from adjustText import adjust_text



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
    
    council = state_councils[0]  # Use first council if multiple
    
    # Find data for this state
    state_jobs = jobs_data[(jobs_data['state'] == state)]
    state_value = value_added_data[(value_added_data['state'] == state)]

    
    # Get license data for this state
    state_licenses = df[df['state'] == state]['paid_holders'].values
    if len(state_licenses) > 0:
        license_value = state_licenses[0]  # Use the first value
    else:
        continue
    
    if len(state_jobs) > 0:
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
           labelspacing=1.2)     # Increase spacing between legend items

# Add labels and title
plt.xlabel('Licenses', fontweight='bold', fontsize=24)
plt.ylabel('Jobs', fontweight='bold',fontsize=24)  # Changed from Income ($) to Jobs
plt.title('Fishery Economic Impact on Jobs by State, \nRecreational Sector (2022)', fontsize=28, fontweight='bold')

# Add grid lines
plt.grid(True, linestyle='--', alpha=0.7)
max_x = plot_df['licenses'].max() * 1.1  # Add 10% buffer
max_y = plot_df['jobs'].max() * 1.1  # Add 10% buffer
# Since y axis is now jobs instead of income, we may need to adjust the y-axis limits
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

# Add the caption
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.figtext(0.60, -0.02, "Note: The size of the bubble represents the landing values of 2022.", ha='right', fontsize=16, style='italic')



# Add reference line
max_x_for_line = plot_df['licenses'].max() * 1.1  # Same buffer as used for xlim
x_line = np.linspace(0, max_x_for_line, 100)
y_line = 0.05 * x_line
plt.plot(x_line, y_line, color='red', linestyle='--', linewidth=2) ##label='y = 0.1x'

plt.text(max_x/2, max_y/1.2, "Jobs equals 5% licenses holders", ha='center', fontsize=20, alpha=0.7)

# Format the axes with commas for thousands
from matplotlib.ticker import FuncFormatter
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, p: '{:,}'.format(int(y))))  # Changed from currency to integer format

# Save and show
plt.tight_layout()
plt.savefig('result/fishery_state_recreational_impact_jobs.png', dpi=300, bbox_inches='tight')
plt.show()


