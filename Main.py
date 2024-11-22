import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import openai
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Define Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# OpenAI API Key
openai.api_key = st.secrets["openai"]["api_key"]

def authenticate_gmail_with_oauth():
    """
    Authenticate Gmail API using OAuth for deployed Streamlit app.
    Includes detailed debugging for tracing errors.
    """
    try:
        logging.debug("Initializing OAuth flow")
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": st.secrets["oauth_credentials"]["client_id"],
                    "client_secret": st.secrets["oauth_credentials"]["client_secret"],
                    "auth_uri": st.secrets["oauth_credentials"]["auth_uri"],
                    "token_uri": st.secrets["oauth_credentials"]["token_uri"],
                    "redirect_uris": [st.secrets["oauth_credentials"]["redirect_uri"]],
                }
            },
            scopes=SCOPES
        )

        # Generate an OAuth authorization URL
        logging.debug("Generating OAuth authorization URL")
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.write("### Step 1: Authenticate Gmail")
        st.write(f"Click [here]({auth_url}) to log in and authorize the app.")
        st.write("After logging in, copy and paste the authorization code below:")

        # Input field for the authorization code
        code = st.text_input("Enter the authorization code")
        if st.button("Submit Authorization Code"):
            logging.debug("Fetching token using authorization code")
            flow.fetch_token(code=code)
            creds = flow.credentials
            logging.debug(f"Token fetched successfully: {creds.token}")
            service = build('gmail', 'v1', credentials=creds)
            st.success("Authentication successful!")
            return service
    except Exception as e:
        st.error(f"OAuth Authentication failed: {e}")
        logging.error(f"OAuth Authentication failed: {e}")
        return None

def fetch_google_alerts(service, query="subject:Google Alert"):
    """
    Fetch Google Alerts emails using Gmail API.
    Includes detailed debugging for tracing errors.
    """
    try:
        logging.debug(f"Searching for Gmail messages with query: {query}")
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        logging.debug(f"Found {len(messages)} messages matching the query")

        email_bodies = []
        for msg in messages:
            logging.debug(f"Fetching email with ID: {msg['id']}")
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = message.get('snippet', '')
            email_bodies.append(snippet)

        st.success(f"Fetched {len(email_bodies)} Google Alert(s).")
        return email_bodies
    except Exception as e:
        st.error(f"Failed to fetch Google Alerts: {e}")
        logging.error(f"Failed to fetch Google Alerts: {e}")
        return []

def summarize_alerts_with_openai(alerts):
    """
    Summarize Google Alerts using OpenAI API.
    Includes detailed debugging for tracing errors.
    """
    try:
        logging.debug("Combining fetched alerts for summarization")
        combined_alerts = "\n".join(alerts)
        logging.debug("Sending alerts to OpenAI for summarization")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following Google Alerts and categorize them:\n\n{combined_alerts}",
            max_tokens=500,
            temperature=0.7
        )
        summary = response.choices[0].text.strip()
        st.success("Summarization completed!")
        logging.debug("Summarization completed successfully")
        return summary
    except Exception as e:
        st.error(f"Failed to summarize alerts: {e}")
        logging.error(f"Failed to summarize alerts: {e}")
        return ""

# Streamlit App Layout
st.title("Google Alerts Summarizer")
st.write("This app fetches Google Alerts emails and summarizes them using OpenAI.")

# Step 1: Authenticate Gmail API
st.subheader("Step 1: Authenticate with Gmail")
logging.debug("Starting Gmail authentication process")
service = authenticate_gmail_with_oauth()

# Step 2: Fetch Google Alerts
if service:
    st.subheader("Step 2: Fetch Google Alerts")
    query = st.text_input("Search Query", value="subject:Google Alert")

    if st.button("Fetch Alerts"):
        logging.debug("Fetching Google Alerts")
        alerts = fetch_google_alerts(service, query=query)

        # Step 3: Summarize Alerts
        if alerts:
            st.subheader("Step 3: Summarize Alerts")
            if st.button("Summarize"):
                logging.debug("Summarizing fetched alerts")
                summary = summarize_alerts_with_openai(alerts)
                st.subheader("Summary")
                st.text_area("Google Alerts Summary", value=summary, height=300)
