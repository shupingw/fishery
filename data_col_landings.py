# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:58:29 2025

@author: ShupingWang
"""


#%%
## Section 1. Pre-process the data: rename, data type, and check
import pandas as pd

landings = pd.read_csv(r'data/FOSS_landings.csv')
landings = landings[['Year', 'Region Name', 'Pounds', 'Dollars', 'Collection']]

value_names = {'Year': 'year',
               'Region Name': 'region',
               'Pounds': 'pounds',
               'Dollars': 'dollars',
               'Collection': 'sector'
    }

landings = landings.rename(columns = value_names)

# Using str.replace to remove commas
landings['pounds'] = landings['pounds'].str.replace(',', '').astype(float)
landings['dollars'] = landings['dollars'].str.replace(',', '').astype(float)

landings = landings.dropna()


value_counts = landings['region'].value_counts()
print("Count of each region:")
print(value_counts)

## Output:
##     Region Name
##     Alaska             74
##     Gulf               74
##     Middle Atlantic    74
##     New England        74
##     Pacific Coast      74
##     South Atlantic     74
##     Great Lakes        48
##     Hawaii             43

print('The maximum of year is', landings['year'].max())
print('The maximum of year is', landings['year'].min())

#%%
## Section 2. Adjust for the inflation
cpi = pd.read_excel(r'data/SeriesReport-20250503122118_127e15.xlsx')

cpi = cpi[['Year', 'Annual']]
cpi = cpi.rename(columns={'Year': 'year', 'Annual':'annual'})

merged_data = landings.merge(cpi, on='year', how='left')

# Choose a base year (e.g., 2023 for current dollars)
base_year = 2023
base_cpi = merged_data[merged_data['year'] == base_year]['annual'].values[0]

# Calculate the adjustment factor
merged_data['cpi_adjustment_factor'] = base_cpi / merged_data['annual']

merged_data['dollars_adjusted'] = merged_data['dollars']*merged_data['cpi_adjustment_factor']

landings = merged_data
#%%
## Section 3. Assign the council id to the landing data

# Create a dictionary mapping FIPS codes to Fishery Management Council IDs
region_to_council = {
    'Alaska': 6,  # Alabama
    'Gulf': 4,  # Alaska
    'Middle Atlantic': 2,  # Arizona
    'New England': 1,  # Arkansas
    'Pacific Coast': 5,  # California
    'South Atlantic': 3,  # Colorado
    'Great Lakes': 9,  # Connecticut
    'Hawaii': 8,  # Delaware
}

# Create a dictionary to map council IDs to council names
council_names = {
    0: 'No Council',
    1: 'New England',
    2: 'Mid-Atlantic',
    3: 'South Atlantic',
    4: 'Gulf of Mexico',
    5: 'Pacific',
    6: 'North Pacific',
    7: 'Caribbean',
    8: 'Western Pacific',
    9: 'Great Lakes'
}



# Create new columns with default values
landings['council_id'] = 'Unknown'
landings['council_name'] = 'Unknown'

# Iterate through each row and assign values
for index, row in landings.iterrows():
    region_value = row['region']
    if region_value in region_to_council:
        landings.loc[index, 'council_id'] = region_to_council[region_value]
        landings.loc[index, 'council_name'] = council_names.get(region_to_council[region_value], 'Unknown')
#%%
## Section 3. Save the data

landings.to_csv(r'data/landings.csv', index=False)
print("Exported to 'landings.csv'")
