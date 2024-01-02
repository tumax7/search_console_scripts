from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
import pandas as pd
from datetime import datetime

# define general constants for google console
API_SERVICE_NAME = "webmasters"
API_VERSION = "v3"
SCOPE = ["https://www.googleapis.com/auth/webmasters.readonly"]
KEY_FILE = "{{path to your api key}}"


def auth_using_key_file(key_filepath: str) -> Resource:
    """Authenticate using a service account key file saved locally"""

    credentials = service_account.Credentials.from_service_account_file(
        key_filepath, scopes=SCOPE
    )
    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    return service

# filepath location of your service account key json file

# authenticate session
service = auth_using_key_file(key_filepath=KEY_FILE)

# verify your service account has permissions to your domain
service.sites().list().execute()

def google_console_call(service,start_date = "2023-09-07",max_rows = 25000, dimensions = ["date","country"]):
    end_date = datetime.now().strftime("%Y-%m-%d")
    response_rows = []
    i = 0
    while True:

        # https://developers.google.com/webmaster-tools/v1/searchanalytics/query
        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": max_rows,
            "startRow": i * max_rows,
        }

        # make request to API
        response = service.searchanalytics().query(siteUrl="sc-domain:{{domain of your website}}", body=payload).execute()

        # if there are rows in the response append to the main list
        if response.get("rows"):
            response_rows.extend(response["rows"])
            i += 1
        else:
            break

    df = pd.DataFrame(response_rows)
    if df.shape[0]:
        for i in range(len(df['keys'].iloc[0])):
            df[dimensions[i]] = df['keys'].apply(lambda x:x[i])

        df = df.drop('keys',axis=1)

    return df

