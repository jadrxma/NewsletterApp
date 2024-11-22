import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import openai

# Set up OpenAI API
openai.api_key = st.secrets["openai"]["api_key"]

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_with_oauth():
    """
    Authenticate Gmail API using OAuth.
    Reads credentials from Streamlit secrets.
    """
    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": st.secrets["oauth_credentials"]["client_id"],
                    "client_secret": st.secrets["oauth_credentials"]["client_secret"],
                    "auth_uri": st.secrets["oauth_credentials"]["auth_uri"],
                    "token_uri": st.secrets["oauth_credentials"]["token_uri"],
                    "redirect_uris": [st.secrets["oauth_credentials"]["redirect_uri"]],
                }
            },
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        service = build('gmail', 'v1', credentials=creds)
        st.success("Authenticated using OAuth.")
        return service
    except Exception as e:
        st.error(f"OAuth Authentication failed: {e}")
        return None

def fetch_google_alerts(service, query="subject:Google Alert"):
    """
    Fetch Google Alerts emails using Gmail API.
    """
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
    """
    Summarize Google Alerts using OpenAI API.
    """
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

# Streamlit App UI
st.title("Google Alerts Summarizer")
st.write("This app fetches Google Alerts emails and summarizes them using OpenAI.")

# Step 1: Authenticate Gmail API
st.subheader("Step 1: Authenticate with Gmail")
service = None
if st.button("Authenticate"):
    service = authenticate_gmail_with_oauth()

# Step 2: Fetch Google Alerts
if service:
    st.subheader("Step 2: Fetch Google Alerts")
    query = st.text_input("Search Query", value="subject:Google Alert")
    
    if st.button("Fetch Alerts"):
        alerts = fetch_google_alerts(service, query=query)
        
        if alerts:
            st.write("Fetched Alerts:")
            for alert in alerts:
                st.write(f"- {alert}")

            # Step 3: Summarize Alerts
            st.subheader("Step 3: Summarize Alerts")
            if st.button("Summarize"):
                summary = summarize_alerts_with_openai(alerts)
                st.subheader("Summary")
                st.text_area("Google Alerts Summary", value=summary, height=300)
