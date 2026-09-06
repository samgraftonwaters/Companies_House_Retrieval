import pandas as pd
import numpy as np
from datetime import datetime

from General_Company_Info import Call_API_Functions as CAF

import configparser
import ast
config = configparser.ConfigParser()
config.read("src/config.ini")

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
        overview_df.to_csv(f'saved_tables/Company_Overview_Table_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(overview_df)

if __name__ == '__main__':

    companies = ast.literal_eval(config['COMPANIES']['companies'])
    url = config['LINKS']['url']
    api_key = config['LINKS']['api_key']
    save_file = config.getboolean('SAVEFILES', 'save_file')

    get_overview_data(companies = companies, url = url, api_key = api_key, save_file = save_file)