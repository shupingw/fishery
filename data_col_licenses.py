# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:58:54 2025

@author: ShupingWang
"""


import pandas as pd
import geopandas as gpd
#%%
## Section 1: pre-process data, rename, check missing data, mathc with fips data
licenses = pd.read_csv(r'data/Table_B._License_Hol_1745938908712.csv')

print(licenses.columns.tolist())
## Ouput:['Year', 'Place Name', 'Paid Fishing License Holders', 
## 'Resident Fishing Licenses, Tags, Permits and Stamps', 
##'Non-Resident Fishing Licenses,\nTags, Permits and Stamps', 
##'Gross Cost ($2024) - Fishing Licenses', 
## 'Cost ($2024)- Resident Fishing Licenses,Tags, Permits and Stamps', 
## 'Cost ($2024) - Non-Resident Fishing Licenses,Tags, Permits and Stamps']

variables = {'Year': 'year',
             'Place Name': 'state',
             'Paid Fishing License Holders': 'paid_holders',
             'Resident Fishing Licenses, Tags, Permits and Stamps' : 'resident_licenses',
             'Non-Resident Fishing Licenses,\nTags, Permits and Stamps': 'nonresident_licenses',
             'Gross Cost ($2024) - Fishing Licenses': 'gross_cost',
             'Cost ($2024)- Resident Fishing Licenses,Tags, Permits and Stamps': 'resident_cost',
             'Cost ($2024) - Non-Resident Fishing Licenses,Tags, Permits and Stamps': 'nonresident_cost'
             
    }

licenses = licenses.rename(columns = variables)

print(licenses['year'].dtype)
## Output: object

licenses['year'] = licenses['year'].astype(str)
licenses['year'] = licenses['year'].str[:4]
licenses['year'] = licenses['year'].astype(int)


print(licenses['year'].dtype)
## Output: int32



print(licenses.columns.tolist())
## Output: ['year', 'state', 'paid_holders', 'resident_licenses', 
##'nonresident_licenses', 'gross_cost', 'resident_cost', 'nonresident_cost']

value_counts = licenses['state'].value_counts()
print("Count of each state:")
print(value_counts)

value_counts = licenses['year'].value_counts()
print("Count of each year:")
print(value_counts)
## year is from 1960 to 2025


## match with fips data
state_fips = pd.read_csv('data/national_state2020.txt', sep='|')  
state_fips.to_csv('data/state_fips.csv')
state_fips = state_fips.rename(columns={'STATEFP': 'fips', 'STATE_NAME': 'state'})
licenses['state'] = licenses['state'].str.title()
value_counts = licenses['state'].value_counts()
print("Count of each state:")
print(value_counts)
## All state names are lower caise not. Now need to replace the name for N. Mariana Islands

licenses['state'] = licenses['state'].replace("N. Mariana Islands", "Commonwealth of the Northern Mariana Islands")
licenses['state'] = licenses['state'].replace("U.S. Virgin Islands", "United States Virgin Islands")
licenses['state'] = licenses['state'].replace("District Of Columbia", "District of Columbia")

licenses = licenses.merge(
    state_fips[['fips', 'state']], 
    on='state',                      
    how='left'                      
)



value_counts = licenses['fips'].value_counts()
print("Count of each state:")
print(value_counts)

na_by_column = licenses.isna().sum()
print("NA count by column:")
print(na_by_column)

#%%
## Section 2: merge with council id and name
## Section 2.1: merge with state population data match state name with fips
##pop = pd.read_csv('pop7017.csv')

##pop['fips'] = pop['fips'].astype(object)

##licenses = licenses.merge(
##    pop[['fips', 'pop', 'year']], 
##    on=['fips', 'year'],                      
##    how='left'                      
##)


value_counts = licenses['fips'].value_counts()
print("Count of each state:")
print(value_counts)

na_by_column = licenses.isna().sum()
print("NA count by column:")
print(na_by_column)


licenses = licenses.dropna(subset=['paid_holders'])

#%%
## Section 2.2: match fips with council name and id
df = pd.read_csv(r'data/fips_council_mapping.csv')

fips_to_council = dict(zip(df['fips'], df['council_id']))
council_names = dict(zip(df['council_id'], df['council_name']))

licenses['council_id'] = 'Unknown'
licenses['council_name'] = 'Unknown'

# Iterate through each row and assign values
for index, row in licenses.iterrows():
    fips = row['fips']
    if fips in fips_to_council:
        licenses.loc[index, 'council_id'] = fips_to_council[fips]
        licenses.loc[index, 'council_name'] = council_names.get(fips_to_council[fips], 'Unknown')

value_counts = licenses['council_name'].value_counts()
print("Count of each state:")
print(value_counts)

value_counts = licenses['council_id'].value_counts()
print("Count of each state:")
print(value_counts)

licenses.to_csv(r'data/licenses.csv', index = False)