from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_with_oauth():
    """Authenticate Gmail API using OAuth."""
    try:
        # Use the credentials.json file downloaded from Google Cloud Console
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

st.title("Google Alerts Summarizer")
st.write("This app fetches Google Alerts emails and summarizes them.")

# Authenticate via OAuth
service = authenticate_gmail_with_oauth()

if service:
    st.subheader("Step 2: Fetch Google Alerts")
    query = st.text_input("Search Query", value="subject:Google Alert")
    
    if st.button("Fetch Alerts"):
        alerts = fetch_google_alerts(service, query=query)
        
        if alerts:
            st.write("Fetched Alerts:")
            st.write(alerts)
