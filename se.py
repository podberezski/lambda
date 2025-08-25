import azure.functions as func
import json
import logging
import os
from azure.communication.email import EmailClient
from azure.communication.email.models import EmailAddress, EmailContent, EmailMessage, EmailRecipients

app = func.FunctionApp()

@app.route(route="sendEmails", methods=["POST"])
def send_emails(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        # Get environment variables
        connection_string = os.environ.get('COMMUNICATION_SERVICES_CONNECTION_STRING')
        sender_address = os.environ.get('SENDER_EMAIL_ADDRESS')
        
        if not connection_string or not sender_address:
            return func.HttpResponse(
                json.dumps({"error": "Missing configuration"}),
                status_code=500,
                headers={'Content-Type': 'application/json'}
            )
        
        # Parse request body
        req_body = req.get_json()
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON"}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )
        
        emails = req_body.get('emails', [])
        link = req_body.get('link', '')
        
        if not emails or not link:
            return func.HttpResponse(
                json.dumps({"error": "Missing emails or link"}),
                status_code=400,
                headers={'Content-Type': 'application/json'}
            )
        
        # Create email client
        email_client = EmailClient.from_connection_string(connection_string)
        
        # Prepare recipients
        recipients = [EmailAddress(email=email) for email in emails]
        
        # Create email message
        email_message = EmailMessage(
            sender=sender_address,
            recipients=EmailRecipients(to=recipients),
            content=EmailContent(
                subject="Shared Link",
                plain_text=f"Please find the link: {link}",
                html=f'<p>Please find the link: <a href="{link}">{link}</a></p>'
            )
        )
        
        # Send email
        poller = email_client.begin_send(email_message)
        
        return func.HttpResponse(
            json.dumps({"message": "Emails sent successfully"}),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logging.error(f"Error sending emails: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to send emails"}),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )
