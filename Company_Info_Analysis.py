import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF
import Overview
import People


api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = []

def get_company_info():

    Overview.overview_data(companies = companies, url = url, api_key = api_key)
    
    officer_data = People.get_officers_data(companies = companies, url = url, api_key = api_key, save_file = False)
    People.get_significant_control_data(companies = companies, url = url, api_key = api_key, save_file = False)
    People.count_people_per_orgs(people_details_df = officer_data, save_file = False)


if __name__ == '__main__':

    get_company_info()