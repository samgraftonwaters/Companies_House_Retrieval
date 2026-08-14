import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF
import Overview


api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = []

def get_company_info():

    Overview.overview_data(companies = companies, url = url, api_key = api_key)



if __name__ == '__main__':

    get_company_info()