import logging

from twilio.rest import Client

from Constant import Constant


def notify_message(message, type):
    client = Client(Constant.TWILIO_ACCOUNT_SID, Constant.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        body=type + message,
        from_='whatsapp:+14155238886',
        to='whatsapp:+918334812477')

    logging.info(message)
