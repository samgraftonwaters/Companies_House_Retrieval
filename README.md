# Companies House Retrieval
**Date:** 7 September 2026

This aim of this Repository is to obtain information about companies registered through Companies House (https://www.gov.uk/government/organisations/companies-house) automatically. Here, multiple companies or differenty types of information can be saved using the scripts within this repository, reducing the manual workload.

For each Company on the Companies House website, there will be a set of tabs that contain different types of date. For example, the usual set of tabs for each Company to click through are shown here,
![The usual set of tabs for each Company to click through to see different types of information](CH_Tabs.png)
but for some companies there may also be an 'Insolvency' tab.
![For some companies there may also be an 'Insolvency' tab](CH_Tabs_Insolvency.png)

The scripts created in this Repository use APIs to call the relavent information from these tabs and saves them in a csv file. Each tab will have its own csv file (or many depending on the different types of detail), but if multiple companies are explored, they will all be within the same table.

The scripts are split into two sections, Finances and other Information. These are discribed below.

## Finances


## Other Information


## How to use this Repository
The main script to run is **'Main.py'**. Here it will call the main functions in the **'Finance_Data_Analysis.py'** and **'Company_Info_Analysis'**, which subsequently run the functions in their respective scripts. Altenatively, you can run either of the **'Finance_Data_Analysis.py'** or **'Company_Info_Analysis'** scripts, or the individual scripts, e.g. if you just wanted to get the Overview data you can run the **'Overview.py'** script.

Before running a script however, you will need to update the variables in the **config.ini** file.

### Config File
The parameters in the **config.ini** file are outlined below, along with their description and expected values.

| Parameter | Description | Expected/Example Values |
| --- | --- | --- |
input_filename | Name of input file (csv) that contains the Companies House numbers (and addition Company's information). If this is set to 'None', it will call the list parameter (see below) | None, company_details |
column_name_company_number | Name of the column that contains the Company House numbers | None Company_House_Numbers |
companies_list  | Alteratively to a csv file, you can put the Company House numbers in a list. Put each number within quotations | ['12345678', '12345679', '12345670'] |
number_of_years | Number of years worth of financial data (if available) | 5, 10, 1 |
url | URL link to call APIs | https://api.company-information.service.gov.uk/company/
api_key | API authentication credentials to be sent with each request. Unique to each individual and can be created at https://developer.company-information.service.gov.uk | **UNIQUE CODE**
save_file | If True, the scripts will save the respective output files (csv) with the relavent data and information| True/False

## Package requirements
The **'requirements.txt'** file contains the required package versions for this Repository. The version of Python to create these scripts was **Version 3.12.7**. To install the required packages, run the following:
***pip install -r requirements.txt***

Alternatively, you can run the conda environment (yml file) using: 

***conda env create -f environment.yml***

***conda activate Companies_House_Retrieval***

