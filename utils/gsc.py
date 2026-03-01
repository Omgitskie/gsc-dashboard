import streamlit as st
import pandas as pd
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from utils.classify import classify_query
from utils.sheets import load_classifications


@st.cache_resource
def get_credentials():
    credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=[
            "https://www.googleapis.com/auth/webmasters.readonly",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
    )
    return credentials


@st.cache_resource
def get_gsc_service():
    try:
        credentials = get_credentials()
        service = build("searchconsole", "v1", credentials=credentials)
        return service
    except Exception as e:
        st.error(f"GSC connection error: {e}")
        return None


@st.cache_data(ttl=3600)
def fetch_gsc_data(start_date, end_date):
    service = get_gsc_service()
    if not service:
        return pd.DataFrame()

    property_url = st.secrets["gsc"]["property_url"]

    try:
        response = service.searchanalytics().query(
            siteUrl=property_url,
            body={
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query", "date"],
                "rowLimit": 25000,
                "dataState": "final"
            }
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            return pd.DataFrame()

        manual = load_classifications()

        data = []
        for row in rows:
            query = row["keys"][0]
            date_val = row["keys"][1]
            segment, store = classify_query(query, manual)
            data.append({
                "query": query,
                "date": date_val,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
                "segment": segment,
                "store": store
            })

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df

    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return pd.DataFrame()
