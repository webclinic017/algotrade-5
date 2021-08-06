from twilio.rest import Client

def SendLog(log):

    account_sid = 'ACbaab0719ce7e14a1866c8c710f280e78' 
    auth_token = '817d401a9f008cd5b8e67d74723b9a22'

    try:
        client = Client(account_sid, auth_token) 
        client.messages.create(from_='whatsapp:+14155238886', body=log,to='whatsapp:+918667764106')
    except Exception as e:
        print(f"Send Log Exception: {e}")

    print(f'\n{log}\n')