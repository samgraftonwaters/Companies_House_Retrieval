import requests
import pandas as pd
import numpy as np
import time

def call_api(url, api_key, company_number, company_info):
    
    response = requests.get(url = url + company_number + company_info, auth = (api_key, ""))
    time.sleep(0.05)
    
    if response.status_code not in (200, 201):
        return(None)
    else:
        return(response.json())


def call_additional_details(url, api_key):
    
    response = requests.get(url = "https://api.company-information.service.gov.uk" + url, auth = (api_key, ""))
    time.sleep(0.1)
    
    if response.status_code not in (200, 201):
        return(None)
    else:
        return(response.json())
    

def pulling_overview_data(company_house_numbers : list, url : str, api_key : str):
    
    """
    Obtain the overview data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        company_house_numbers (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing overview details from an API call
    """

    required_columns = ['company_name', 'company_number', 'company_status', 'company_status_detail', 'date_of_creation', 'has_charges', 
                    'has_insolvency_history', 'registered_office_is_in_dispute', 'accounts_last_accounts_period_end_on', 
                    'accounts_last_accounts_period_start_on', 'accounts_next_due', 'accounts_overdue', 'accounts_next_accounts_overdue', 
                    'confirmation_statement_next_due', 'confirmation_statement_overdue', 'registered_office_address_address_line_1', 
                    'registered_office_address_address_line_2', 'registered_office_address_country', 'registered_office_address_locality', 
                    'registered_office_address_postal_code', 'registered_office_address_region', 'sic_codes']

    companies = []
    
    for i in range(len(company_house_numbers)):
    
        output = call_api(url = url, api_key = api_key, company_number = company_house_numbers[i], company_info = '')
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")
    
            df = df.reindex(columns=required_columns).iloc[[0]]
            
            companies.append(df)
            
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Company Name', 'Company Number', 'Company Status', 'Status Details', 'Creation Date', 'Has Charges', 'Has Insolvency History',
                  'Registered Office in Dispute', 'Last Accounts Period End On', 'Last Accounts Period Start On', 'Accounts Next Due', 'Accounts Overdue',
                  'Next Accounts Overdue', 'Confirmation Statement Next Due', 'Confirmation Statement Overdue', 'Address Line 1', 'Address Line 2', 
                  'Address Country', 'Address City', 'Postcode', 'County', 'SIC Codes']

    return(df)


def pulling_people_data(company_house_numbers : list, url : str, api_key : str):

    """
    Obtain People's data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        company_house_numbers (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing People's details from an API call
    """

    required_columns = ['appointed_on', 'is_pre_1992_appointment', 'name', 'officer_role', 'person_number', 'address_address_line_1', 
                        'address_address_line_2', 'address_locality', 'address_postal_code', 
                        'identity_verification_details_appointment_verification_statement_due_on', 'resigned_on', 'links_self', 
                        'links_officer_appointments']#, 'Resigned', 'Active', 'CompanyNumber']
    
    companies = []
    
    for i in range(len(company_house_numbers)):
    
        output = call_api(url = url, api_key = api_key, company_number = company_house_numbers[i], company_info = '/officers')
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            items_df = pd.json_normalize(df.loc[0, "items"], sep = '_')
    
            items_df = items_df.reindex(columns=required_columns)

            items_df['Resigned'] = np.where(items_df['resigned_on'].isna() == True, False, True)
            items_df['Active'] = np.where(items_df['resigned_on'].isna() == True, True, False)
            items_df['CompanyNumber'] = company_house_numbers[i]
            
            companies.append(items_df)
            
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Appointed On', 'Pre 1992 Appointment', 'Name (Officers)', 'Officer Role', 'Person Number', 'Address Line 1 (Officers)', 'Address Line 2 (Officers)', 'Address City (Officers)', 
                  'Postcode (Officers)', 'Identity Verification Statement Due', 'Resigned on', 'Officer Links', 'Appointment Links', 'Resigned (Officers)', 
                  'Active (Officers)', 'Company Number']

    df['Pre 1992 Appointment'] = df['Pre 1992 Appointment'].astype('bool')

    return(df)


def pulling_sig_control_data(company_house_numbers : list, url : str, api_key : str):

    """
    Obtain people with significant control data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        company_house_numbers (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing persons with significant control details from an API call
    """
        
    required_columns = ['notified_on', 'ceased_on', 'name', 'name_elements_forename', 
                        'name_elements_surname', 'address_address_line_1', 'address_address_line_2', 'address_country', 'address_locality', 
                        'address_postal_code', 'address_premises', 'ceased', 'kind', 'natures_of_control', 
                       'identity_verification_details_appointment_verification_statement_date', 
                       'identity_verification_details_appointment_verification_statement_due_on', 'links_self', 'Active']
    
    companies = []
    
    for i in range(len(company_house_numbers)):
    
        output = call_api(url = url, api_key = api_key, company_number = company_house_numbers[i], company_info = '/persons-with-significant-control')
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            items_df = pd.json_normalize(df.loc[0, "items"], sep = '_')

            items_df = items_df.reindex(columns=required_columns)

            # items_df['Active'] = np.where(items_df['ceased_on'].isna() == True, True, False)
            items_df['CompanyNumber'] = company_house_numbers[i]
            
            companies.append(items_df)
            
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Notified On', 'Ceased On', 'Name (Significant Control)', 'Forename (Significant Control)', 
                  'Surname (Significant Control)', 'Address Line 1 (Significant Control)',
                  'Address Line 2 (Significant Control)', 'Address Country (Significant Control)', 'Address City (Significant Control)', 
                  'Postcode (Significant Control)', 'Address Premises (Significant Control)', 'Ceased', 'Kind of Control', 
                  'Nature of Control', 'Identity Verification Statement Due From',
                  'Identity Verification Statement Due By', 'Person with Significant Control Links', 'Active (Significant Control)', 'Company Number']

    return(df)


def pulling_charge_data(company_house_numbers : list, url : str, api_key : str):

    """
    Obtain the charges data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        company_house_numbers (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing charges details from an API call
    """
        
    required_columns = ['charge_code', 'charge_number', 'status', 'delivered_on',
                           'created_on', 'persons_entitled', 'transactions', 'classification_type',
                           'classification_description', 'particulars_type', 'particulars_description',
                           'particulars_contains_floating_charge', 'particulars_contains_fixed_charge', 
                           'particulars_floating_charge_covers_all', 'particulars_contains_negative_pledge']
    
    companies = []
    
    for i in range(len(company_house_numbers)):
    
        output = call_api(url = url, api_key = api_key, company_number = company_house_numbers[i], company_info = '/charges')
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            items_df = pd.json_normalize(df.loc[0, "items"], sep = '_')
    
            items_df = items_df.reindex(columns=required_columns)
            
            items_df['CompanyNumber'] = company_house_numbers[i]
            
            companies.append(items_df)
            
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Charge Code', 'Charge Number', 'Status', 'Delivered On', 'Created On', 'Persons Entitled', 'Transactions', 'Classification Type',
                 'Classification Description', 'Particulars Type', 'Brief Description', 'Contains Floating Charge?', 'Contains Fixed Charge?', 
                  'Floating Charge Covers All?', 'Contains Negative Pledge?', 'Company Number']

    return(df)

def pulling_transactions_data(charges_df, api_key : str):

    """
    Obtain the transactions data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        charges_df (DataFrame): data frame containing the charges data
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing transactions details from an API call
    """

    required_columns = ['type', 'date', 'category', 'subcategory',
       'description', 'action_date', 'description_values_charge_number']
    
    df = charges_df[['Transactions']]
    df = df.explode("Transactions")
    expanded = pd.json_normalize(df["Transactions"])
    expanded.columns = ['Type', 'Delivered On', 'Link']
    expanded
    
    companies = []
    
    for i in range(len(charges_df)):

        url = expanded['Link'][i]
        company_number = charges_df['Company Number'][i]

        if pd.isna(url) or not isinstance(url, str):
            continue
    
        output = call_additional_details(url = url, api_key = api_key)
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            df = df.reindex(columns=required_columns)

            df['Company Number'] = company_number

            companies.append(df)
    
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Type', 'Date', 'Category', 'Subcategory', 'Description', 'Action Date', 'Charge Code', 'Company Number']

    return(df)

def pulling_additional_data(data_table, url : str, api_key : str):

    """
    Obtain the additional data for each company and their respective details using an API call.
    Required columns are those deemed most important to be taken from the API table
    
    Parameters:
    -----------
        data_table (DataFrame)): dataframe containing data regarding officers/people at each company
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing additional details for people/officers from an API call
    """

    required_columns = ['appointed_on', 'name', 'is_pre_1992_appointment', 'officer_role',
       'address_address_line_1', 'address_address_line_2', 'address_country',
       'address_locality', 'address_postal_code', 'address_premises',
       'appointed_to_company_name', 'appointed_to_company_number',
       'appointed_to_company_status',
       'name_elements_forename', 'name_elements_title',
       'name_elements_other_forenames', 'name_elements_surname',
       'identity_verification_details_appointment_verification_end_on',
       'identity_verification_details_appointment_verification_start_on',
       'resigned_on']
    
    companies = []
    
    for i in range(len(data_table)):

        url = data_table['Appointment Links'][i]
      
        output = call_additional_details(url = url, api_key = api_key)
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            items_df = pd.json_normalize(df.loc[0, "items"], sep = '_')
    
            items_df = items_df.reindex(columns=required_columns)
            
            companies.append(items_df)
            
    df = pd.concat(companies, ignore_index=True)

    df.columns = ['Appointed On', 'Name (Person Details)', 'Pre 1992 Appointment (Person Details)', 'Officer Role (Person Details)',
                  'Address Line 1 (Person Details)', 'Address Line 2 (Person Details)', 'Address Country (Person Details)', 
                  'Address City (Person Details)', 'Postcode (Person Details)', 'Address Premises (Person Details)',
                  'Company Name', 'Company Number', 'Company Status', 'Forename (Person Details)', 'Title', 'Other Names (Person Details)',
                  'Surname (Person Details)', 'Identity Verification End On', 'Identity Verification Start On', 'Resigned on']

    df['Pre 1992 Appointment (Person Details)'] = df['Pre 1992 Appointment (Person Details)'].astype('bool')

    return(df)

def pulling_insolvency_data(company_house_numbers : list, url : str, api_key : str):

    """
    Obtain the insolvency data for each company and their respective details using an API call.
    
    Parameters:
    -----------
        company_house_numbers (list|series): list or dataframe column containing company house numbers
        url (str): main url path for companies house website
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/

    Returns:
    --------
        DataFrame: dataframe containing insolvency details from an API call
    """

    insolvency_dates = []
    insolvency_prac = []

    for i in range(len(company_house_numbers)):

        company_number = company_house_numbers[i]

        output = call_api(url = url, api_key = api_key, company_number = company_number, company_info = '/insolvency')
    
        if output is None:
            continue
        
        else:
            df = pd.json_normalize(output, sep="_")

            items_df = pd.json_normalize(df.loc[0, "cases"], sep = '_')

            for j in range(len(items_df)):
                items_df_dates = pd.json_normalize(items_df.loc[j, "dates"], sep = '_')
                items_df_prac = pd.json_normalize(items_df.loc[j, "practitioners"], sep = '_')
            
                items_df_dates['Type'] = items_df['type'][j]
                items_df_dates['Number'] = items_df['number'][j]
                items_df_dates['Company Number'] = company_number
            
                items_df_prac['Type'] = items_df['type'][j]
                items_df_prac['Number'] = items_df['number'][j]
                items_df_prac['Company Number'] = company_number

                insolvency_dates.append(items_df_dates)
                insolvency_prac.append(items_df_prac)

    if not insolvency_dates:
        print('No Companies with Insolvency Dates')
        insolvency_dates = pd.DataFrame(None)
    else:
        insolvency_dates = pd.concat(insolvency_dates, ignore_index=True)
        insolvency_dates.columns = ['Insolvency Time Period', 'Date', 'Insolvency Type', 'Insolvency Number', 'Company Number']

    if not insolvency_prac:
        print('No Companies with Insolvency Practices')
        insolvency_prac = pd.DataFrame(None)
    else:   
        insolvency_prac = pd.concat(insolvency_prac, ignore_index=True)
        insolvency_prac = insolvency_prac.drop(['address_locality', 'address_region', 'address_postal_code', 'address_address_line_1', 'address_line_2', 'ceased_to_act_on'], axis = 1, errors='ignore')
        insolvency_prac = insolvency_prac.rename(columns = {'name' : 'Practitioner Name', 'role' : 'Role', 'Type' : 'Insolvency Type', 'Number' : 'Insolvency Number', 'appointed_on' : 'Appointed On'})
 
    return(insolvency_dates, insolvency_prac)
    