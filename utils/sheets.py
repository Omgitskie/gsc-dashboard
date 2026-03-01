import streamlit as st
import pandas as pd
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build


@st.cache_resource
def get_sheets_service():
    try:
        credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=[
                "https://www.googleapis.com/auth/webmasters.readonly",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
        )
        service = build("sheets", "v4", credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Sheets connection error: {e}")
        return None


def load_classifications():
    try:
        service = get_sheets_service()
        sheet_id = st.secrets["sheets"]["sheet_id"]
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:C"
        ).execute()
        values = result.get("values", [])
        if len(values) <= 1:
            return {}
        padded = [row + [""] * (3 - len(row)) for row in values[1:]]
        df = pd.DataFrame(padded, columns=["query", "segment", "store"])
        df = df[df["segment"] != ""]
        df["store"] = df["store"].replace("", None)
        return dict(zip(df["query"], zip(df["segment"], df["store"])))
    except Exception as e:
        st.warning(f"Could not load classifications: {e}")
        return {}


def save_classification(query, segment, store=None):
    try:
        service = get_sheets_service()
        sheet_id = st.secrets["sheets"]["sheet_id"]
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:C"
        ).execute()
        values = result.get("values", [])
        row_index = None
        for i, row in enumerate(values):
            if row and row[0] == query:
                row_index = i + 1
                break
        store_val = store if store else ""
        new_row = [query, segment, store_val]
        if row_index:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"Sheet1!A{row_index}:C{row_index}",
                valueInputOption="RAW",
                body={"values": [new_row]}
            ).execute()
        else:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="Sheet1!A:C",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": [new_row]}
            ).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Could not save classification: {e}")
        return False


def delete_classification(query):
    try:
        service = get_sheets_service()
        sheet_id = st.secrets["sheets"]["sheet_id"]
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:C"
        ).execute()
        values = result.get("values", [])
        for i, row in enumerate(values):
            if row and row[0] == query:
                service.spreadsheets().values().clear(
                    spreadsheetId=sheet_id,
                    range=f"Sheet1!A{i+1}:C{i+1}"
                ).execute()
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Could not delete classification: {e}")
        return False


def export_unclassified_to_sheet(other_df):
    try:
        service = get_sheets_service()
        sheet_id = st.secrets["sheets"]["sheet_id"]
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range="Sheet1!A:A"
        ).execute()
        existing = [row[0] for row in result.get("values", []) if row]
        new_rows = [
            [row["query"], "", ""]
            for _, row in other_df.iterrows()
            if row["query"] not in existing
        ]
        if new_rows:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="Sheet1!A:C",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": new_rows}
            ).execute()
        return len(new_rows)
    except Exception as e:
        st.error(f"Export failed: {e}")
        return 0
