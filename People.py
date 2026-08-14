import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF

def get_officers_data(companies, url, api_key, save_file = False):

    people_full_df = CAF.pulling_people_data(iterative_range = len(companies), company_house_numbers = companies, url = url,  api_key = api_key)
    print(len(people_full_df))
    print(people_full_df.info())
    print(people_full_df.head(5))

    people_df = people_full_df.copy()
    people_df = people_df[['Company Number', 'Person Number', 'Name (Officers)', 'Officer Role', 'Appointed On', 'Pre 1992 Appointment', 'Identity Verification Statement Due',
                        'Resigned on', 'Resigned (Officers)', 'Active (Officers)']]

    people_df[['Surname (Officers)', 'Forename (Officers)']] = people_df['Name (Officers)'].str.split(',', n=1, expand=True)

    print(people_df.head(5))

    if save_file == True:
        people_df.to_csv('Org_Officers_Table.csv', sep = ',', index = False)

    return(people_df)


def get_significant_control_data(companies, url, api_key, save_file = False):

    sig_control_full_df = CAF.pulling_sig_control_data(iterative_range = len(companies), company_house_numbers = companies, url = url,  api_key = api_key)

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
        sig_control_df.to_csv('Org_Sig_Control_Table.csv', sep = ',', index = False)

    return(sig_control_df)


def count_people_per_orgs(people_details_df, save_file = False):

    people_orgs_df = people_details_df.copy()
    people_orgs_df = people_orgs_df[['Name (Person Details)', 'Officer Role (Person Details)', 'Company Number', 'Company Status', 'Resigned (Person Details)']]
    people_orgs_df = people_orgs_df.rename(columns = {'Name (Person Details)' : 'Name', 'Officer Role (Person Details)' : 'Role',
                                                    'Resigned (Person Details)' : 'Resigned'})
    print(people_orgs_df.head(5))

    count_role = people_orgs_df.groupby(['Name', 'Role']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()
    print(count_role.head(5))

    count_orgs = people_orgs_df.groupby(['Name'])['Company Number'].count().reset_index()
    count_orgs.columns = ['Name', 'Number of Associated Companies']

    print(count_orgs.head(5))

    count_status = people_orgs_df.groupby(['Name', 'Company Status']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()

    count_status.columns = ['Name', 'Status: Actice', 'Status: Administration', 'Status: Disolved', 'Status: Liquidation']
    print(count_status.head(5))

    count_resigned = people_orgs_df.groupby(['Name', 'Resigned']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()
    count_resigned.columns = ['Name', 'Active', 'Resigned']
    print(count_resigned.head(5))

    merge_1 = pd.merge(count_orgs, count_role, on = 'Name', how = 'left')

    merge_2 = pd.merge(count_status, count_resigned, on = 'Name', how = 'left')

    people_orgs_count = pd.merge(merge_1, merge_2, on = 'Name', how = 'left')
    print(people_orgs_count.columns)

    print(people_orgs_count.head(5))

    if save_file == True:
        people_orgs_count.to_csv('Count_Org_People_Assigned.csv', sep = ',', index = False)

    return(people_orgs_count)