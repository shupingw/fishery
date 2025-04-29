# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:53:05 2025

@author: ShupingWang
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os


#%%
## Section 1. read two dataset
licenses = pd.read_csv(r'data/licenses.csv')


#%%
## Section 2. Join two datasets based on state
state = gpd.read_file("data/tl_2019_us_state.zip")
state = state.to_crs(epsg=4326)
state = state.rename(columns={'STATEFP': 'fips'})
licenses['fips'] = licenses['fips'].astype(str).str.zfill(2)
state['fips'] = state['fips'].astype(str).str.zfill(2)

merged = licenses.merge(state, on='fips', how='left')


# Check if the merge was successful
print(f"Original licenses records: {len(licenses)}")
print(f"Merged records: {len(merged)}")
print(f"Records with missing geometry: {merged['geometry'].isna().sum()}")

#%%
## not useful if not include population data
merged['total_pc'] = merged['paid_holders']/merged['pop']
merged['res_pc'] = merged['resident_licenses']/merged['pop']
merged['nonres_pc'] = merged['nonresident_licenses']/merged['pop']

state_averages = merged.groupby('state')['total_pc'].mean().reset_index()
state_averages = merged.groupby('state')['res_pc'].mean().reset_index()
state_averages = merged.groupby('state')['nonres_pc'].mean().reset_index()

# Now you can use to_file
#%%
na_by_column = merged.isna().sum()
print("NA count by column:")
print(na_by_column)

## Section 2. Export
gdf = gpd.GeoDataFrame(merged, geometry='geometry', crs="EPSG:4326")
gdf.to_file(r'data/licenses.gpkg', layer="licenses", driver="GPKG")