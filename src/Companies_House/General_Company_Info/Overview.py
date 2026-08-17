import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF

def get_overview_data(companies, url, api_key, save_file = False):

    overview_full_df = CAF.pulling_overview_data(iterative_range = len(companies), company_house_numbers = companies, url = url,  api_key = api_key)

    bool_cols = ['Accounts Overdue', 'Next Accounts Overdue', 'Confirmation Statement Overdue']
    overview_full_df[bool_cols]  = overview_full_df[bool_cols].astype(bool).where(overview_full_df[bool_cols].notna())

    print(len(overview_full_df))
    print(overview_full_df.info())

    overview_df = overview_full_df.copy()
    overview_df = overview_df[['Company Number', 'Company Name', 'Company Status', 'Creation Date', 'Has Charges', 
                                            'Has Insolvency History', 'Registered Office in Dispute', 'Accounts Next Due', 'Accounts Overdue',
                                            'Next Accounts Overdue', 'Confirmation Statement Next Due', 'Confirmation Statement Overdue']]
    print(overview_df.head())

    if save_file == True:
        overview_df.to_csv('Company_Overview_Table.csv', sep = ',', index = False)

    return(overview_df)