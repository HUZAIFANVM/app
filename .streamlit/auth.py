import os
import requests
import urllib.parse
from dotenv import load_dotenv
import streamlit as st
load_dotenv("D:\\intern\\data-analytics-auditor-tool\\.env")

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
SCOPE = " ".join([
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
])


AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)

def exchange_code_for_tokens(code):
    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(TOKEN_URL, data=token_data)

    if response.ok:
        return response.json()
    else:
        raise Exception(f"Token exchange failed: {response.text}")

def refresh_access_token(refresh_token):
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(TOKEN_URL, data=payload)

    if response.ok:
        return response.json()
    else:
        raise Exception(f"Refresh failed: {response.text}")
