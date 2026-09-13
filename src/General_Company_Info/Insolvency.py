import pandas as pd
from datetime import datetime

from General_Company_Info import Call_API_Functions as CAF

import configparser
import ast
config = configparser.ConfigParser()
config.read("src/config.ini")

def get_insolvency_data(companies : list, url : str, api_key : str, save_file : bool = False):

    """
    Obtain any insolvency details and information about a company.
    
    Parameters:
    -----------
        companies (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing insolvency details of each company if present.
    """

    insolvency_dates, insolvency_practitioners = CAF.pulling_insolvency_data(company_house_numbers = companies, url = url,  api_key = api_key)

    if not insolvency_dates.empty:
        number_insolvencies = insolvency_dates.groupby(['Company Number'])['Insolvency Number'].max().reset_index(name = 'Total Number Insolvencies')
        number_insolvencies.columns = ['Companies House Number', 'Total Number Insolvencies']
        number_insolvencies_types = insolvency_dates.groupby(['Company Number', 'Insolvency Type']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()
    else:
        number_insolvencies_types = None
        number_insolvencies = None

    if not insolvency_practitioners.empty:
        number_practitioners = insolvency_practitioners.groupby(['Company Number'])['Practitioner Name'].count().reset_index(name = 'Total Number Practitioners')
        number_role = insolvency_practitioners.groupby(['Company Number', 'Role']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()
    else:
        number_practitioners = None
        number_role = None

    dfs = [number_insolvencies, number_insolvencies_types, number_practitioners, number_role]

    if all(df is None for df in dfs):
        insolvency_metrics = None
    else:
        dfs = [df for df in dfs if df is not None]
        merged = pd.concat(dfs, axis=1)
        merged = merged.drop('Company Number', axis=1)
        insolvency_metrics = merged.rename({'Companies House Number': 'Company Number'}, axis=1)

        if save_file == True:
            insolvency_metrics.to_csv(f'src/General_Company_Info/saved_tables/Count_Insolvency_Details_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)
            insolvency_practitioners.to_csv(f'src/General_Company_Info/saved_tables/Insolvency_Practitioners_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)
            insolvency_dates.to_csv(f'src/General_Company_Info/saved_tables/Insolvency_Dates_Types_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    print('Insolvency Analysis Completed')
    return(insolvency_metrics)

if __name__ == '__main__':

    if config['INPUT']['input_filename'] != 'None':
        data = pd.read_csv(f'src/input_data_tables/{config['INPUT']['input_filename']}.csv')
        companies_number_col_name = config['INPUT']['column_name_company_number']
        companies = data[companies_number_col_name].astype("string")

    else:
        companies = ast.literal_eval(config['INPUT']['companies_list'])
    url = config['LINKS']['url']
    api_key = config['LINKS']['api_key']
    save_file = config.getboolean('SAVEFILES', 'save_file')

    get_insolvency_data(companies = companies, url = url, api_key = api_key, save_file = save_file)


