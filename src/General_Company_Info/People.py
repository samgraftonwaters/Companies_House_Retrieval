import pandas as pd
import numpy as np
from datetime import datetime

from General_Company_Info import Call_API_Functions as CAF

import configparser
import ast
config = configparser.ConfigParser()
config.read("src/config.ini")

def get_officers_data(companies : list, url : str, api_key : str, save_file : bool = False):

    """
    Obtain the Officers for each company and their respective details
    
    Parameters:
    -----------
        companies (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing Officer details for each company in the companies list or series
    """

    people_full_df = CAF.pulling_people_data(company_house_numbers = companies, url = url,  api_key = api_key)

    people_df = people_full_df.copy()
    people_df = people_df[['Company Number', 'Person Number', 'Name (Officers)', 'Officer Role', 'Appointed On', 'Pre 1992 Appointment', 'Identity Verification Statement Due',
                        'Resigned on', 'Resigned (Officers)', 'Active (Officers)']]

    people_df[['Surname (Officers)', 'Forename (Officers)']] = people_df['Name (Officers)'].str.split(',', n=1, expand=True)

    if save_file == True:
        people_df.to_csv(f'src/General_Company_Info/saved_tables/Company_Officers_Table_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(people_df)


def get_significant_control_data(companies : list, url : str, api_key : str, save_file : bool = False):

    """
    Obtain the people with significant control at each company and their respective details
    
    Parameters:
    -----------
        companies (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing people with significant control details for each company in the companies list or series
    """
    sig_control_full_df = CAF.pulling_sig_control_data(company_house_numbers = companies, url = url,  api_key = api_key)

    sig_control_full_df['Ceased'] = sig_control_full_df['Ceased'].astype(bool).where(sig_control_full_df['Ceased'].notna())

    sig_control_df = sig_control_full_df.copy()
    sig_control_df = sig_control_df[['Company Number', 'Name (Significant Control)', 'Forename (Significant Control)', 
                                 'Surname (Significant Control)', 'Notified On', 'Ceased On', 'Ceased', 'Kind of Control',
                                 'Nature of Control', 'Identity Verification Statement Due From', 'Identity Verification Statement Due By']]

    sig_control_df['Surname (Significant Control)'] = sig_control_df['Surname (Significant Control)'].str.upper()

    if save_file == True:
        sig_control_df.to_csv(f'src/General_Company_Info/saved_tables/Company_Sig_Control_Table_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(sig_control_df)

def get_peoples_details(companies : list, url : str, api_key : str, save_file : bool = False):

    """
    Obtain the people's additional information and details at each company and their respective details
    
    Parameters:
    -----------
        companies (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing people's additional details for each company in the companies list or series
    """

    data_table = CAF.pulling_people_data(company_house_numbers = companies, url = url,  api_key = api_key)

    people_details_full_df = CAF.pulling_additional_data(data_table = data_table, url = url,  api_key = api_key)

    people_details_df = people_details_full_df.copy()

    people_details_df = people_details_df [['Name (Person Details)', 'Forename (Person Details)', 'Surname (Person Details)', 
                                        'Officer Role (Person Details)', 'Company Number', 'Company Name', 'Company Status', 
                                        'Appointed On', 'Pre 1992 Appointment (Person Details)', 'Identity Verification End On', 
                                        'Identity Verification Start On', 'Resigned on']]

    people_details_df['Resigned (Person Details)'] = np.where(people_details_df['Resigned on'].isna() == True, False, True)
    people_details_df.head(5)

    if save_file == True:
        people_details_df.to_csv(f'src/General_Company_Info/saved_tables/Org_Sig_Control_Current_Previous_Orgs_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    print('People Analysis Completed')
    return(people_details_df)


def get_count_people_per_orgs(people_details_df, save_file = False):

    """
    Count the number of companies associated with each person

    Parameters:
    -----------
        people_details_df (dataframe): dataframe containing people's details
        save_file (bool): determines whether the final table can be saved to a csv file. Default = False
    
    Returns:
    --------
        DataFrame: dataframe containing how many companies each person is associated with
    """

    people_orgs_df = people_details_df.copy()

    people_orgs_df = people_orgs_df[['Name (Person Details)', 'Officer Role (Person Details)', 'Company Number', 'Company Status', 'Resigned (Person Details)']]
    people_orgs_df = people_orgs_df.rename(columns = {'Name (Person Details)' : 'Name', 'Officer Role (Person Details)' : 'Role',
                                                    'Resigned (Person Details)' : 'Resigned'})

    count_role = people_orgs_df.groupby(['Name', 'Role']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()

    count_orgs = people_orgs_df.groupby(['Name'])['Company Number'].count().reset_index()
    count_orgs.columns = ['Name', 'Number of Associated Companies']

    expected_statuses = ['active', 'administration', 'dissolved', 'liquidation']
    count_status = people_orgs_df.groupby(['Name', 'Company Status']).size().unstack(fill_value=0).reindex(columns=expected_statuses, fill_value=0).reset_index()

    count_status.columns = ['Name', 'Status: Actice', 'Status: Administration', 'Status: Disolved', 'Status: Liquidation']

    count_resigned = people_orgs_df.groupby(['Name', 'Resigned']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()
    count_resigned.columns = ['Name', 'Active', 'Resigned']

    merge_1 = pd.merge(count_orgs, count_role, on = 'Name', how = 'left')

    merge_2 = pd.merge(count_status, count_resigned, on = 'Name', how = 'left')

    people_orgs_count = pd.merge(merge_1, merge_2, on = 'Name', how = 'left')

    if save_file == True:
        people_orgs_count.to_csv(f'src/General_Company_Info/saved_tables/Count_Company_People_Assigned_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(people_orgs_count)

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

    get_officers_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    get_significant_control_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    peoples_details = get_peoples_details(companies = companies, url = url, api_key = api_key, 
                                          save_file = save_file)
    get_count_people_per_orgs(people_details_df = peoples_details, save_file = save_file)