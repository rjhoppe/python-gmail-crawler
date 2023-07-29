import time
import os
import sys
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Import all necessary Google API libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Pull MacroDroid Webhook URL
load_dotenv()
md_url = os.getenv("MD_WEBHOOK_URL")

# Start time for timeout capabilities
current_time = datetime.now()
task_end_time = current_time + timedelta(hours = 8)
loops = 0

# Pulled from Google Python quickstart.py file
SCOPES = ['https://mail.google.com/']

def gen_gcp_api():
    
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

creds = gen_gcp_api()

# Check for new mail every 15 minutes
def get_email():

    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    query = 'in:inbox is:unread -category:(promotions OR social)'
    include_spam = False

    max_results = 3
    results = service.users().messages().list(userId='me', includeSpamTrash=include_spam, 
                                              maxResults=max_results, q=query).execute()
    messages = results.get('messages')

    # Initialize dict for job related subjects / senders
    job_update_dict = {}

    for msg in messages:
        
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        try:
            payload = txt['payload']
            msg_id = msg['id']
            # print(msg_id)
            headers = payload['headers']

            for d in headers:
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']

            catchword = 'Steam'
            if catchword in subject:
                print('Found a relevant email!')
                new_dict = {sender: subject}
                job_update_dict.update(new_dict)
                # Mark message as unread after parsed
                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
                # print('Marked as unread!')

        except:
            print('Something went wrong...')
            sys.exit()

    if len(job_update_dict) > 0 and loops > 0:
        return send_notification(relevant_emails=job_update_dict)
    elif len(job_update_dict) > 0:
        return job_update_dict 
    else:
        print('Nothing found, will check again in 15.')
        time.sleep(900)
        if datetime.now() < task_end_time:
            get_email()
        else:
            sys.exit()

relevant_emails = get_email()


def send_notification(relevant_emails):
        
    print('Sending notification...')
    
    for k, v in relevant_emails.items():

        webhookurl = md_url+f'?Subject={v}&Sender={k}'
 
        response = requests.post(webhookurl)

        print(response, 'Notification sent')
    
    if datetime.now() < task_end_time:
        time.sleep(900)
        global loops 
        loops += 1
        return get_email()
    else:
        sys.exit()

send_notification(relevant_emails)


# Final tasks
# Doc string the functions
# Change the trigger word
# Create requirements.txt
# Turn into an .exe file