import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email import message_from_bytes
import openai
from datetime import datetime

# Set OpenAI API Key
openai.api_key = ""

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_api():
    """Authenticate and create a Gmail API service."""
    creds = None
    # Load credentials from file
    if st.secrets["credentials_file"]:
        creds = Credentials.from_authorized_user_info(st.secrets["credentials_file"], SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_google_alerts(service, start_date):
    """Fetch Google Alerts emails after the specified date."""
    query = f"subject:Google Alert after:{start_date.strftime('%Y/%m/%d')}"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    email_bodies = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        parts = payload.get('parts', [])
        
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                data = part['body']['data']
                decoded_data = base64.urlsafe_b64decode(data).decode()
                email_bodies.append(decoded_data)
    return email_bodies

def summarize_alerts_with_openai(alerts):
    """Summarize Google Alerts using OpenAI."""
    combined_alerts = "\n".join(alerts)
    response = openai.Completion.create(
        engine="text-davinci-003",  # Or gpt-4 if available
        prompt=f"Summarize the following Google Alerts and organize them into categories: \n\n{combined_alerts}",
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Streamlit App
st.title("Google Alerts Summarizer")
st.write("This app fetches your Google Alerts emails and summarizes them using OpenAI.")

# Step 1: Authenticate Gmail API
st.subheader("Step 1: Authenticate with Gmail")
if "gmail_service" not in st.session_state:
    if st.button("Authenticate Gmail"):
        try:
            st.session_state["gmail_service"] = authenticate_gmail_api()
            st.success("Gmail authenticated successfully!")
        except Exception as e:
            st.error(f"Authentication failed: {e}")

# Step 2: Fetch Google Alerts
if "gmail_service" in st.session_state:
    st.subheader("Step 2: Fetch Google Alerts")
    start_date = st.date_input("Start Date", value=datetime.now())
    
    if st.button("Fetch Alerts"):
        try:
            alerts = fetch_google_alerts(st.session_state["gmail_service"], start_date)
            if alerts:
                st.session_state["alerts"] = alerts
                st.success(f"Fetched {len(alerts)} alerts.")
            else:
                st.warning("No alerts found.")
        except Exception as e:
            st.error(f"Failed to fetch alerts: {e}")

# Step 3: Summarize Alerts
if "alerts" in st.session_state:
    st.subheader("Step 3: Summarize Alerts")
    if st.button("Summarize"):
        try:
            summary = summarize_alerts_with_openai(st.session_state["alerts"])
            st.session_state["summary"] = summary
            st.success("Alerts summarized successfully!")
        except Exception as e:
            st.error(f"Failed to summarize alerts: {e}")

# Display Summary
if "summary" in st.session_state:
    st.subheader("Summary")
    st.text_area("Google Alerts Summary", value=st.session_state["summary"], height=300)

