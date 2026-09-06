from General_Company_Info import Overview
from General_Company_Info import People
from General_Company_Info import Charges_Transactions as CT
from General_Company_Info import Insolvency

import configparser
import ast
config = configparser.ConfigParser()
config.read("src/config.ini")

def get_company_info(companies, url, api_key, save_file = False):

    Overview.get_overview_data(companies = companies, url = url, api_key = api_key, save_file = save_file)

    People.get_officers_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    People.get_significant_control_data(companies = companies, url = url, api_key = api_key, save_file = save_file)
    peoples_details = People.get_peoples_details(companies = companies, url = url, api_key = api_key, save_file = save_file)
    People.get_count_people_per_orgs(people_details_df = peoples_details, save_file = save_file)

    charges = CT.get_charges_data(companies, url, api_key, save_file = save_file)
    transactions = CT.get_transactions_data(charges = charges, api_key = api_key, save_file = save_file)
    charges_transactions_merged = CT.merge_charges_transactions(charges, transactions, save_file = save_file)
    number_of_charges = CT.get_number_charges(charges, save_file = save_file)

    Insolvency.get_insolvency_data(companies, url, api_key, save_file = save_file)

if __name__ == '__main__':

    companies = ast.literal_eval(config['COMPANIES']['companies'])
    url = config['LINKS']['url']
    api_key = config['LINKS']['api_key']
    save_file = config.getboolean('SAVEFILES', 'save_file')

    get_company_info(companies = companies, url = url, api_key = api_key, save_file = save_file)