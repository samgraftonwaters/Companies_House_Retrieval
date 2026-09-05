import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF

api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = ['12773942', '11481000', '09752181', '05035690', '03712506', '02516363', '04860838', 
             '11210637', '06987042', '01588942', '02740580', '02582268', '10921663', '10623473', 
             '03864182', '02404983', '08313240', '10622354', '12043446', '11558635', '05852516', 
             '06976037', '05167623', '08445134', '11452512', '05714286', '05271676', '07883905', 
             '12299608', '03053472']

def get_overview_data(companies : list, url : str, api_key : str, save_file : bool = False):

    """
    Obtain the overview and general details of each company
    
    Parameters:
    -----------
        companies (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing the overall details of each company.
    """

    overview_full_df = CAF.pulling_overview_data(company_house_numbers = companies, url = url,  api_key = api_key)

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

if __name__ == '__main__':

    get_overview_data(companies = companies, url = url, api_key = api_key, save_file = True)