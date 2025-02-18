import gspread
from oauth2client.service_account import ServiceAccountCredentials
import constants.constants as cts
import pandas as pd
import os
import shutil

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(cts.CREDENTIALS_FILE, scope)

def get_data(credentials, spreadsheet_key, sheet_name):
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_key)
    worksheet = spreadsheet.worksheet(sheet_name)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def move_previous_data(filename, bkp_folder):
    if not os.path.exists(bkp_folder):
        os.makedirs(bkp_folder)
    if os.path.exists(filename):
        today = pd.Timestamp.today().strftime('%Y%m%d-%H%M%S')
        shutil.move(filename, os.path.join(bkp_folder, f"data_{today}.csv"))

def clean_bk_folder(bkp_folder):
    if os.path.exists(bkp_folder):
        files = [os.path.join(bkp_folder, f) for f in os.listdir(bkp_folder) if os.path.isfile(os.path.join(bkp_folder, f))]
        if len(files) > 10:
            files.sort(key=lambda x: os.path.getmtime(x))
            oldest_file = files[0]
            os.remove(oldest_file)

def save_new_data(df: pd.DataFrame):
    df.to_csv(cts.DATA_FILENAME, index=False)

if __name__ == "__main__":
    move_previous_data(cts.DATA_FILENAME, cts.DATA_BKP_FOLDER)
    clean_bk_folder(cts.DATA_BKP_FOLDER)
    df = get_data(credentials, cts.SPREAD_ID, cts.SHEET_NAME)
    save_new_data(df)