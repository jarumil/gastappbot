import gspread
from oauth2client.service_account import ServiceAccountCredentials
import constants.constants as cts
import pandas as pd
import os
import shutil
import json

def get_data(credentials, spreadsheet_key, sheet_name):
    """
    Retrieve data from a Google Sheets spreadsheet.

    Parameters
    ----------
    credentials : ServiceAccountCredentials
        Google API credentials.
    spreadsheet_key : str
        The key of the spreadsheet.
    sheet_name : str
        The name of the sheet to retrieve data from.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the spreadsheet data.
    """
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_key)
    worksheet = spreadsheet.worksheet(sheet_name)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df

def move_previous_data(filename, bkp_folder):
    """
    Move the previous data file to a backup folder.

    Parameters
    ----------
    filename : str
        The name of the file to move.
    bkp_folder : str
        The backup folder path.
    """
    if not os.path.exists(bkp_folder):
        os.makedirs(bkp_folder)
    if os.path.exists(filename):
        today = pd.Timestamp.today().strftime('%Y%m%d-%H%M%S')
        shutil.move(filename, os.path.join(bkp_folder, f"data_{today}.csv"))

def clean_bk_folder(bkp_folder):
    """
    Clean the backup folder by removing the oldest file if there are more than 10 files.

    Parameters
    ----------
    bkp_folder : str
        The backup folder path.
    """
    if os.path.exists(bkp_folder):
        files = [os.path.join(bkp_folder, f) for f in os.listdir(bkp_folder) if os.path.isfile(os.path.join(bkp_folder, f))]
        if len(files) > 10:
            files.sort(key=lambda x: os.path.getmtime(x))
            oldest_file = files[0]
            os.remove(oldest_file)

def save_new_data(df: pd.DataFrame, filename: str):
    """
    Save new data to a CSV file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the new data.
    filename : str
        The name of the file to save the data to.
    """
    if not os.path.exists(cts.DATA_FOLDER):
        os.makedirs(cts.DATA_FOLDER)
    df.to_csv(filename, date_format='%d/%m/%Y', index=False)

if __name__ == "__main__":
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(cts.CREDENTIALS_FOLDER, cts.CREDENTIALS_FILE), scope)

    with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE)) as f:
        api_credentials = json.load(f)

    with open("config.json", "r") as f:
        config = json.load(f)

    move_previous_data(os.path.join(cts.DATA_FOLDER, cts.DATA_FILENAME), cts.DATA_BKP_FOLDER)
    clean_bk_folder(cts.DATA_BKP_FOLDER)
    df = get_data(credentials, api_credentials["spreadsheet_id"], config["sheet_data_name"])
    save_new_data(df, os.path.join(cts.DATA_FOLDER, cts.DATA_FILENAME))