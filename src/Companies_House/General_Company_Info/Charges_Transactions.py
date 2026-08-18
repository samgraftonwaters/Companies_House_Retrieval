import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF

def get_charges_data(companies, url, api_key, save_file = False):

    charges = CAF.pulling_charge_data(iterative_range = len(companies), company_house_numbers = companies, url = url,  api_key = api_key)

    charges['Charge Number'] = charges['Charge Number'].astype(int)
    print(charges.head(5))

    if save_file == True:
        charges.to_csv('Company_Charges_Table.csv', sep = ',', index = False)
    return(charges)

def get_transactions_data(charges, api_key, save_file = False):

    transactions = CAF.pulling_transactions_data(iterative_range = len(charges), charges_df = charges, api_key = api_key)

    print(transactions.head(5))
    if save_file == True:
        transactions.to_csv('Company_Transactions_Table.csv', sep = ',', index = False)
    return(transactions)

def merge_charges_transactions(charges, transactions, save_file = False):

    charges = charges.drop(['Transactions', 'Persons Entitled', 'Classification Type', 'Particulars Type'], axis = 1)
    transactions = transactions.drop(['Company Number'], axis = 1)
    
    charges_transactions = pd.merge(charges, transactions, on = 'Charge Code', how = 'left')
    charges_transactions.head(2)

    if save_file == True:
        charges_transactions.to_csv('Company_Charges_Transactions_Table.csv', sep = ',', index = False)

    return(charges_transactions)


def get_number_charges(charges, save_file = False):

    number_charges = charges.copy()
    number_charges = number_charges.drop(['Charge Code', 'Delivered On', 'Created On', 'Persons Entitled', 'Transactions', 'Classification Type', 
                                      'Particulars Type', 'Brief Description', 'Contains Floating Charge?',
                                      'Contains Fixed Charge?', 'Floating Charge Covers All?', 'Contains Negative Pledge?'], axis = 1).reset_index(drop = True)

    max_number_charges = number_charges.groupby(['Company Number'])['Charge Number'].max().reset_index(name = 'Total Number Charges')
    number_charges = pd.merge(number_charges, max_number_charges, on = 'Company Number', how = 'left')


    count_outstanding_charges = (number_charges.groupby(['Company Number', 'Status']).size().unstack(fill_value=0)
                                .reindex(columns=['outstanding', 'fully-satisfied', 'part-satisfied', 'Other (charges)'], fill_value=0).reset_index())

    count_outstanding_charges = count_outstanding_charges.rename(columns = {'outstanding' : 'Outstanding', 'fully-satisfied' : 'Fully Satisfied', 'part-satisfied': 'Part Satisfied'})

    number_charges = pd.merge(number_charges, count_outstanding_charges, on = 'Company Number', how = 'left')

    class_type = (number_charges.groupby(['Company Number', 'Classification Description']).size().unstack(fill_value=0)
                                .reindex(columns=['A registered charge', 'Legal charge', 'Debenture', 'Other (types)'], fill_value=0).reset_index())
    
    number_charges = pd.merge(number_charges, class_type, on = 'Company Number', how = 'left')

    number_charges = number_charges.drop(['Charge Number', 'Status', 'Classification Description'], axis = 1).drop_duplicates(subset = 'Company Number').reset_index(drop = True)

    number_charges['Outstanding Proportion'] = number_charges['Outstanding']/number_charges['Total Number Charges']
    number_charges['Fully-satisfied Proportion'] = number_charges['Fully Satisfied']/number_charges['Total Number Charges']
    number_charges['Part-satisfied Proportion'] = number_charges['Part Satisfied']/number_charges['Total Number Charges']
    number_charges['Other (charges) Proportion'] = number_charges['Other (charges)']/number_charges['Total Number Charges']

    number_charges['Registered Charge Proportion'] = number_charges['A registered charge']/number_charges['Total Number Charges']
    number_charges['Legal Charge Proportion'] = number_charges['Legal charge']/number_charges['Total Number Charges']
    number_charges['Debenture Proportion'] = number_charges['Debenture']/number_charges['Total Number Charges']
    number_charges['Other (types) Proportion'] = number_charges['Other (types)']/number_charges['Total Number Charges']

    print(number_charges.columns)
    print(number_charges.head(5))

    if save_file == True:
        number_charges.to_csv('Company_Number_Prop_Charges.csv',  sep = ',', index = False)

    return(number_charges)