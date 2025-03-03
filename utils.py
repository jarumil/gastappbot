from datetime import datetime
import importlib
from oauth2client.service_account import ServiceAccountCredentials
import requests
import fitz
import os

def get_class_from_string(class_path):
    """
    Import a class from a string path.

    Parameters
    ----------
    class_path : str
        The dot-separated path to the class.

    Returns
    -------
    type
        The class type.
    """
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def download_page_in_pdf(credentials: ServiceAccountCredentials, spreadsheet_id: str, guid: str) -> str:
    """
    Download a page from a Google Spreadsheet in PDF format.

    Parameters
    ----------
    credentials : ServiceAccountCredentials
        The Google API credentials.
    spreadsheet_id : str
        The ID of the Google Spreadsheet.
    guid : str
        The GUID of the page to download.
    """
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=pdf&gid={guid}" \
          "&portrait=false" \
          "&fitw=true" \
          "&scale=2" \
          "&size=A4" \
          "&top_margin=0.25&bottom_margin=0.25&left_margin=0.25&right_margin=0.25" \
          "&gridlines=false" \
          "&printtitle=false" \
          "&sheetnames=false"

    headers = {
        "Authorization": f"Bearer {credentials.get_access_token().access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        full_name = f"dashboard_full_{now}.pdf"
        name = f"dashboard_{now}.png"
        with open(full_name, "wb") as f:
            f.write(response.content)

        pdf_document = fitz.open(full_name)
        page = pdf_document.load_page(0)
        pix = page.get_pixmap(dpi=400)
        pix.save(name)
        pdf_document.close()
        os.remove(full_name)

        return name
    return None
