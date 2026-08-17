import requests
import pandas as pd
import numpy as np
import time

def call_api(url, api_key, company_number, company_info):
    
    response = requests.get(url = url + company_number + company_info, auth = (api_key, ""))
    time.sleep(0.1)
    
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
