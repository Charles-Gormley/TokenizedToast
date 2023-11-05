import openai
import idna
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.text import MIMEText
from article_creation import create_content, create_email_html

import json


def get_gmail_credentials():
    creds = None

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(subject:str, body:str, recipient:str):
    creds = get_gmail_credentials()

    service = build('gmail', 'v1', credentials=creds)

    html_content = body
    message = MIMEText(html_content, 'html')
    message['to'] = recipient
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    body = {'raw': raw}
    

    try:
        message = (service.users().messages().send(userId="me", body=body).execute())
        print('Message Id: %s' % message['id'])
        return 'Email sent!'
    except HttpError as error:
        print('An error occurred: %s' % error)
        return 'Failed to send email'
    


def lambda_handler(event, context):
    # Extract event details
    preferences = event['preferences']
    articles = event['articles']
    email_address = event['email_address']
    request_type = event['request_type'] 

    # Summarize articles with OpenAI
    summarized_articles = []
    for article in articles:
        content_dict = create_content(preferences, article)
        summarized_articles.append(content_dict)

    if request_type == "email":
        email = create_email_html(summarized_articles, preferences, style="light-mode")
 

        # Send the email
        send_email(email['subject'], email['body'], email_address)

        return {
            'statusCode': 200,
            'body': json.dumps('Email sent successfully!')
        }

if __name__ == "__main__":
    send_email("Testing", "Testing", "cgormley07@gmail.com")