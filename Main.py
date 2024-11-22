import streamlit as st
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

# OpenAI API Key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_with_service_account():
    """Authenticate Gmail API using a service account."""
    try:
        credentials = Credentials.from_service_account_info(st.secrets["credentials_file"])
        service = build('gmail', 'v1', credentials=credentials)
        st.success("Authenticated using Service Account.")
        return service
    except Exception as e:
        st.error(f"Service Account Authentication failed: {e}")
        return None

def authenticate_gmail_with_oauth():
    """Authenticate Gmail API using OAuth for user access."""
    try:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        service = build('gmail', 'v1', credentials=creds)
        st.success("Authenticated using OAuth.")
        return service
    except Exception as e:
        st.error(f"OAuth Authentication failed: {e}")
        return None

def fetch_google_alerts(service, query="subject:Google Alert"):
    """Fetch Google Alerts emails using Gmail API."""
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        email_bodies = []
        
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = message.get('snippet', '')
            email_bodies.append(snippet)
        
        st.success(f"Fetched {len(email_bodies)} Google Alert(s).")
        return email_bodies
    except Exception as e:
        st.error(f"Failed to fetch Google Alerts: {e}")
        return []

def summarize_alerts_with_openai(alerts):
    """Summarize Google Alerts using OpenAI API."""
    try:
        combined_alerts = "\n".join(alerts)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following Google Alerts and categorize them:\n\n{combined_alerts}",
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].text.strip()
        st.success("Summarization completed.")
        return summary
    except Exception as e:
        st.error(f"Failed to summarize alerts: {e}")
        return ""

# Streamlit App
st.title("Google Alerts Summarizer")
st.write("This app fetches Google Alerts emails and summarizes them using OpenAI.")

# Select Authentication Method
auth_method = st.selectbox("Choose Authentication Method", ["Service Account", "OAuth"])

if auth_method == "Service Account":
    service = authenticate_gmail_with_service_account()
elif auth_method == "OAuth":
    service = authenticate_gmail_with_oauth()
else:
    service = None

if service:
    st.subheader("Step 2: Fetch Google Alerts")
    query = st.text_input("Search Query", value="subject:Google Alert")
    
    if st.button("Fetch Alerts"):
        alerts = fetch_google_alerts(service, query=query)
        
        if alerts:
            st.subheader("Step 3: Summarize Alerts")
            if st.button("Summarize"):
                summary = summarize_alerts_with_openai(alerts)
                st.subheader("Summary")
                st.text_area("Google Alerts Summary", value=summary, height=300)

