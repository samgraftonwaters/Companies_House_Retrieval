import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF

def get_insolvency_data(companies, url, api_key, save_file = False):

    insolvency_dates, insolvency_practitioners = CAF.pulling_insolvency_data(iterative_range = len(companies), company_house_numbers = companies, url = url,  api_key = api_key)

    number_insolvencies = insolvency_dates.groupby(['Company Number'])['Insolvency Number'].max().reset_index(name = 'Total Number Insolvencies')
    number_insolvencies.columns = ['Companies House Number', 'Total Number Insolvencies']
    number_insolvencies_types = insolvency_dates.groupby(['Company Number', 'Insolvency Type']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()

    number_practitioners = insolvency_practitioners.groupby(['Company Number'])['Practitioner Name'].count().reset_index(name = 'Total Number Practitioners')
    number_role = insolvency_practitioners.groupby(['Company Number', 'Role']).size().unstack(fill_value=0).reindex(fill_value=0).reset_index()

    merged = pd.concat([number_insolvencies, number_insolvencies_types, number_practitioners, number_role], axis = 1)
    merged = merged.drop('Company Number', axis = 1)
    insolvency_metrics = merged.rename({'Companies House Number': 'Company Number'}, axis = 1)

    if save_file == True:
        insolvency_metrics.to_csv('Count_Insolvency_Details.csv', sep = ',', index = False)
        insolvency_practitioners.to_csv('Insolvency_Practitioners.csv', sep = ',', index = False)
        insolvency_dates.to_csv('Insolvency_Dates_Types.csv', sep = ',', index = False)

    return(insolvency_metrics)


