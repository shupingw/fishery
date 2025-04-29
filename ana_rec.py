# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:54:55 2025

@author: ShupingWang
"""



import pandas as pd
from ana_fishery_eco import clean_value

rec_exp = pd.read_csv(r'data/recreational_trip_expenditures.csv')
rec_exp['Trip Expenditure'] = rec_exp['Trip Expenditure'].apply(clean_value)

import pandas as pd

# Define a function to combine Florida regions
def combine_florida_regions(dataframe, area_column='Area', sum_column='Trip Expenditure'):
    df_copy = dataframe.copy()
    # Replace all Florida regions with 'Florida'
    florida_regions = ["Easter Florida", "East Florida", "West Florida"]
    for region in florida_regions:
        df_copy.loc[df_copy[area_column] == region, area_column] = "Florida"

    # Group by area and sum the expenditure
    result_df = df_copy.groupby(area_column).agg({
        sum_column: 'sum'
    }).reset_index()
    return result_df



# If you need to preserve other columns:
def combine_florida_with_other_columns(dataframe, area_column='Area', sum_columns=None)
    if sum_columns is None:
        sum_columns = {'Trip Expenditure': 'sum'}
    
    # Create a copy to avoid modifying the original
    df_copy = dataframe.copy()
    
    # Replace all Florida regions with 'Florida'
    florida_regions = ["Easter Florida", "East Florida", "West Florida"]
    for region in florida_regions:
        df_copy.loc[df_copy[area_column] == region, area_column] = "Florida"
    
    # Group by area and aggregate the specified columns
    result_df = df_copy.groupby(area_column).agg(sum_columns).reset_index()
    
    return result_df

combined_data = combine_florida_regions(rec_exp)


# Usage example with multiple columns:
# combined_data = combine_florida_with_other_columns(
#     df, 
#     sum_columns={
#         'Trip Expenditure': 'sum',
#         'Visitors': 'sum',
#         'Rating': 'mean'
#     }
# )
rec_exp = rec_exp.rename(columns={'Area': 'state'}) 


value_counts = rec_exp['state'].value_counts()
print("Count of each year:")
print(value_counts)
rec_exp_upd = add_council_info(df=rec_exp)

rec_har = pd.read_csv(r'data/recreational_harvest_release.csv')
rec_har = rec_har.rename(columns={'Area': 'state'})
rec_har_upd = add_council_info(df=rec_har)


rec_eff = pd.read_csv(r'data/recreational_effort.csv')
rec_eff = rec_eff.rename(columns={'Area': 'state'})
rec_eff_upd = add_council_info(df=rec_eff)


rec_imp = pd.read_csv(r'data/recreational_impacts_state.csv')
rec_imp = rec_imp.rename(columns={'Area': 'state'})


