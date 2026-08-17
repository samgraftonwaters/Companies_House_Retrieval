import requests
import pandas as pd
import numpy as np
import time

from . import Call_API_Functions as CAF
from . import  Overview
from . import  People
from . import  Charges_Transactions as CT
from . import  Insolvency


api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = ['12773942', '11481000', '09752181', '05035690', '03712506', '02516363', '04860838', '11210637', '06987042', '01588942', '02740580', '02582268', '10921663', '10623473', '03864182',
             '02404983', '08313240', '10622354', '12043446', '11558635', '05852516', '06976037', '05167623', '08445134', '11452512', '05714286', '05271676', '07883905', '12299608', '03053472']


def get_company_info(companies, url, api_key, save_file = False):

    Overview.get_overview_data(companies = companies, url = url, api_key = api_key, save_file = save_file)

    officer_data = People.get_officers_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    People.get_significant_control_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    People.get_count_people_per_orgs(people_details_df = officer_data, save_file = save_file)

    charges = CT.get_charges_data(companies, url, api_key, save_file = save_file)
    transactions = CT.get_transactions_data(charges = charges, save_file = save_file)
    charges_transactions_merged = CT.merge_charges_transactions(charges, transactions, save_file = save_file)
    number_of_charges = CT.get_number_charges(charges, save_file = save_file)

    Insolvency.get_insolvency_data(companies, url, api_key, save_file = save_file)


if __name__ == '__main__':

    get_company_info(companies = companies, url = url, api_key = api_key, save_file = False)