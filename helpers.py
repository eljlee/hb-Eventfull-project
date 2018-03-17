import os

from twilio.rest import Client
ACCOUNT_SID=os.environ['ACCOUNT_SID']
AUTH_TOKEN=os.environ['AUTH_TOKEN']
def send_txt_notification(message, ACCOUNT_SID, AUTH_TOKEN):
    """Send txt notifications."""

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    client.api.account.messages.create(
        to="+14159907366",
        from_="+14158516073 ",
        body="{body}".format(body=message)
    )