import requests
import pandas as pd
import numpy as np
import time

import Call_API_Functions as CAF


api_key = None
url = "https://api.company-information.service.gov.uk/company/"

companies = []