import pandas as pd
import numpy as np
from datetime import datetime

import Call_API_Functions as CAF

api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = ['12773942', '11481000', '09752181', '05035690', '03712506', '02516363', '04860838', 
             '11210637', '06987042', '01588942', '02740580', '02582268', '10921663', '10623473', 
             '03864182', '02404983', '08313240', '10622354', '12043446', '11558635', '05852516', 
             '06976037', '05167623', '08445134', '11452512', '05714286', '05271676', '07883905', 
             '12299608', '03053472']

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
    print(len(people_full_df))
    print(people_full_df.info())
    print(people_full_df.head(5))

    people_df = people_full_df.copy()
    people_df = people_df[['Company Number', 'Person Number', 'Name (Officers)', 'Officer Role', 'Appointed On', 'Pre 1992 Appointment', 'Identity Verification Statement Due',
                        'Resigned on', 'Resigned (Officers)', 'Active (Officers)']]

    people_df[['Surname (Officers)', 'Forename (Officers)']] = people_df['Name (Officers)'].str.split(',', n=1, expand=True)

    print(people_df.head(10))

    if save_file == True:
        people_df.to_csv(f'saved_tables/Company_Officers_Table_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

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

    print(len(sig_control_full_df))
    print(sig_control_full_df.info())
    print(sig_control_full_df.head(5))

    sig_control_full_df['Ceased'] = sig_control_full_df['Ceased'].astype(bool).where(sig_control_full_df['Ceased'].notna())

    sig_control_df = sig_control_full_df.copy()
    sig_control_df = sig_control_df[['Company Number', 'Name (Significant Control)', 'Forename (Significant Control)', 
                                 'Surname (Significant Control)', 'Notified On', 'Ceased On', 'Ceased', 'Kind of Control',
                                 'Nature of Control', 'Identity Verification Statement Due From', 'Identity Verification Statement Due By']]

    sig_control_df['Surname (Significant Control)'] = sig_control_df['Surname (Significant Control)'].str.upper()

    print(sig_control_df.head(5))

    if save_file == True:
        sig_control_df.to_csv(f'saved_tables/Company_Sig_Control_Table_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

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
        people_details_df.to_csv(f'saved_tables/Org_Sig_Control_Current_Previous_Orgs_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

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

    print(people_orgs_df.columns)

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

    print(people_orgs_count.columns)
    print(people_orgs_count.head(5))

    if save_file == True:
        people_orgs_count.to_csv(f'saved_tables/Count_Company_People_Assigned_{datetime.now().strftime('%d-%b-%Y')}.csv', sep = ',', index = False)

    return(people_orgs_count)

if __name__ == '__main__':

    get_officers_data(companies = companies, url = url, api_key = api_key, save_file = True)
    get_significant_control_data(companies = companies, url = url, api_key = api_key, save_file = True)
    peoples_details = get_peoples_details(companies = companies, url = url, api_key = api_key, save_file = True)
    get_count_people_per_orgs(people_details_df = peoples_details, save_file = True)