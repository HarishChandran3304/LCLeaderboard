import requests
from bs4 import BeautifulSoup
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TEST_SPREADSHEET_ID = "1LdFP-nQ-kSeT-sL8Mx7L5pVC5siJDVsf4sbpTWLwhgg"
MAIN_SPREADSHEET_ID = "1V2AmgRmcLf0MB1z2Uf-0tWBMA3rdSj6THXKjmAoRoL0"

credentials = None
if os.path.exists("token.json"):
    credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        credentials = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(credentials.to_json())

TOTAL = 18


def get_values(total):
    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        result = sheets.values().get(spreadsheetId=MAIN_SPREADSHEET_ID, range=f"HANDLES!A2:D{total+1}").execute()
        values = result.get("values", [])
        values = sorted(values, key=lambda x: int(x[3]), reverse=True)

        return values

    except HttpError as error:
        print(error)
    
def check_daily(handle):
    response = requests.get(f'https://leetcode.com/{handle}')
    soup = BeautifulSoup(response.text, 'html.parser')

    div = soup.find_all(class_='lc-md:flex hidden h-auto w-full flex-1 items-center justify-center')[0]
    month = div.find_all("svg")[-1]
    week = month.find_all("g")[-1]
    day = list(week.children)[-1]

    return True if "green" in day.attrs["fill"] else False

def get_total(handle):
    res = requests.get(f'https://leetcodestats.cyclic.app/{handle}').json()
    return res["totalSolved"]

def update_values(values):
    print(values)
    for i in range(len(values)):
        handle = values[i][1]
        values[i][2] = "Yes" if check_daily(handle) else "No"
        values[i][3] = get_total(handle)
        print(values[i])

    return values

def write_values(values, total):
     try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        
        sheets.values().update(spreadsheetId=MAIN_SPREADSHEET_ID, range=f'HANDLES!A2:D{total+1}',
                               valueInputOption="USER_ENTERED", body={"values": values}).execute()

     except HttpError as error:
        print(error)


def main():
    values = get_values(TOTAL)
    values = update_values(values)
    write_values(values, TOTAL)
    

if __name__ == "__main__":
    main()
