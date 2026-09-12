import requests
import pandas as pd
import time
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from html import unescape
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
pd.set_option('display.max_colwidth', None)

"""
Note, some of these functions were created with the help of MS CoPilot
"""

def call_api(url, api_key, company_number, company_info, params = None):

    """
    Uses the Requests package to get the details from the Companies House API

    Parameters:
    -----------
        url (str): url of the HTTP or API to obtain the infomation
        api_key (str): Unique API authentication credentials to be sent with each request
        company_number (str): Company's Companies House registered number
        company_details (str): Details tab name for each company
        params (dict): Used to add query parameters
    
    Returns:
    --------
        The API response as a .json file, if the status of the request is 200 or 201, otherwise nothing.
    
    """
    response = requests.get(url = url + company_number + company_info, params=params, auth = (api_key, ""))
    time.sleep(0.05)
    
    if response.status_code not in (200, 201):
        return(None)
    else:
        return(response.json())


def call_additional_details(url, api_key):

    """
    Uses the Requests package to obtain further details from the Companies House API

    Parameters:
    -----------
        url (str): url of the HTTP or API to obtain the infomation
        api_key (str): Unique API authentication credentials to be sent with each request
    
    Returns:
    --------
        The API response as a .json file, if the status of the request is 200 or 201, otherwise nothing.
    
    """

    response = requests.get(url = url, auth = (api_key, ""))
    time.sleep(0.1)
    
    if response.status_code not in (200, 201):
        return(None)
    else:
        return(response.json())
    

def pull_finance_data_from_api(company_house_numbers : list, url : str, api_key : str):

    """
    Uses the Requests package to get the finacial details from the Companies House API

    Parameters:
    -----------
        company_house_numbers (str): Company's Companies House registered number
        url (str): url of the HTTP or API to obtain the infomation
        api_key (str): Unique API authentication credentials to be sent with each request
    
    Returns:
    --------
        Financial information for each company as a dataframe
    
    """

    required_columns = [
        'type', 'date', 'category', 'description', 'action_date', 'links_document_metadata', 'subcategory', 'paper_filed',
        'description_values_change_date', 'description_values_termination_date', 'description_values_notification_date']

    companies = []

    for i in range(len(company_house_numbers)):

        company_number = company_house_numbers[i]

        all_items = []
        start = 0
        page_size = 25

        while True:
            params = {
                "start_index": start,
                "items_per_page": page_size
            }

            output = call_api(url = url, api_key = api_key, company_number = company_number, params = params, company_info = '/filing-history')

            if not output or output == 'None':
                break
    
            items = output.get("items", [])
            total_count = output.get("total_count", 0)

            if not items:
                break

            all_items.extend(items)
            start += page_size

            if start >= total_count:
                break

        if not all_items:
            continue
            
        items_df = pd.json_normalize(all_items, sep='_')

        items_df = items_df.reindex(columns=required_columns)

        items_df['Company Number'] = company_number

        companies.append(items_df)

    if companies:
        df = pd.concat(companies, ignore_index=True)
    else:
        df = pd.DataFrame(columns=required_columns + ['Company Number'])

    return(df)


def get_formats(doc_meta_url, api_key):

    """
    Determines if the accounts data contains a PDF or IXBRL files.

    Parmeters:
    ----------
        doc_meta_url (str): metadata url link
        api_key (str): Unique API authentication credentials to be sent with each request

    Returns:
    --------
        Series containing columns to whether the data is from a PDF or IXBRL file
    """

    try:

        if pd.isna(doc_meta_url) or not isinstance(doc_meta_url, str):
            return pd.Series({
                "content_url": None,
                "has_pdf": False,
                "has_ixbrl": False
            })

        request = call_additional_details(url=doc_meta_url, api_key=api_key)

        if not isinstance(request, dict):
            raise ValueError("Non-JSON response")

        resources = request.get("resources", {})
        links = request.get('links', {})

        return pd.Series({
            "content_url": links.get("document"),
            "has_pdf": "application/pdf" in resources,
            "has_ixbrl": "application/xhtml+xml" in resources
        })

    except Exception as e:
        print(f"Error for {doc_meta_url}: {e}")
        content_url = doc_meta_url + '/content' if isinstance(doc_meta_url, str) else None
        return pd.Series({
            "content_url": links.get("document"), 
            "has_pdf": False,
            "has_ixbrl": False
        })


def make_ixbrl_reader(content_url, api_key):

    """
    Retrieve the iXBRL content from a URL.

    Parameters:
    ------------
        content_url (str): URL of the IXBRL document to retrieve.
        api_key (str): API key used for authentication.

    Returns:
        A callable that fetches the iXBRL document and returns its text.
    """

    def reader():
        r = requests.get(
            content_url,
            auth=(api_key, ''),
            headers={"Accept": "application/xhtml+xml"}
        )

        return r.text 
    return reader



def get_accounts_data(data, api_key, number_of_years):

    """
    Obtains the financial details

    Parameters:
    -----------
        data (dataframe): datatable that is taken from the Companies House 'filing history' tab
        api_key (str): companies house user unique API key from https://developer.company-information.service.gov.uk/
        number_of_years (int): Number of years the financial data is returned for. For example, if 5, then
        5 years worth of data is obtained

    Returns:
    --------
        accounts list for each company for the number of years requested
    
    """

    accounts_list = []
    
    for i, number in enumerate(data['Company Number'].unique()):
        subset = data[(data['Company Number'] == number) & (data['category'] == 'accounts')].sort_values('date', ascending=False).reset_index(drop = True)
       
        if subset.empty:
            continue

        recent_accounts = subset.copy()

        recent_accounts = recent_accounts.iloc[0:number_of_years,]
        
        recent_accounts["links_document_metadata"] = recent_accounts["links_document_metadata"].astype("string")

        recent_accounts = recent_accounts.dropna(subset=["links_document_metadata"])

        if recent_accounts.empty == True:
            continue
    
        meta_urls = recent_accounts['links_document_metadata'].dropna().unique()
        format_map = {}
        
        for url in meta_urls:
            format_map[url] = get_formats(doc_meta_url = url, api_key = api_key)
        
        format_df = pd.DataFrame.from_dict(format_map, orient='index')
        format_df.index.name = 'links_document_metadata'
        format_df = format_df.reset_index()
        
        recent_accounts = recent_accounts.merge(format_df, on='links_document_metadata', how='left')

        recent_accounts_years = recent_accounts[recent_accounts["has_ixbrl"] == True]
        
        if not recent_accounts_years.empty:
            accounts_list.append(recent_accounts_years)
    

    if accounts_list:
        accounts_update = pd.concat(accounts_list, ignore_index=True)
    else:
        accounts_update = pd.DataFrame()

    return(accounts_update)


def parse_ixbrl(html):

    """
    Get the financial data from the IXBRL HTML

    Parameters:
    -----------
        (html): IXBRL html url for the Company

    Returns:
    --------
        DataFrame with Company's financial data obtained through the IXBRL HTML
    """

    soup = BeautifulSoup(html, "lxml", parse_only = None)

    data = []

    # capture both numeric + nonnumeric
    tags = soup.find_all(["ix:nonfraction", "ix:nonnumeric"], limit= None)

    for tag in tags:
        value = tag.get_text(strip=True)

        # apply scale if present
        scale = tag.get("scale")
        if scale and value.replace('.', '', 1).isdigit():
            value = float(value) * (10 ** int(scale))

        data.append({
            "tag": tag.name,  # ix:nonfraction
            "name": tag.get("name"),  # e.g. AverageNumberEmployeesDuringPeriod
            "value": value,
            "context": tag.get("contextref"),
            "unit": tag.get("unitref"),
            "decimals": tag.get("decimals"),
            "scale": tag.get("scale"),
            "format": tag.get("format"),
            "id": tag.get("id")
        })

    return pd.DataFrame(data)


def parse_html(html):

    """
    Get the financial data from the HTML

    Parameters:
    -----------
        (html): html url for the Company

    Returns:
    --------
        DataFrame with Company's financial data obtained through the HTML
    """

    html = unescape(html)

    html_soup = BeautifulSoup(html, "html.parser")

    divs = html_soup.find_all("div")

    rendered_rows = []

    for div in divs:

        txt = div.get_text(" ", strip=True)

        if not txt:
            continue

        rendered_rows.append(txt)

    rendered_df = pd.DataFrame({
        "source": "rendered_html",
        "row_text": rendered_rows
    })

    return(rendered_df)