import requests


API_TOKEN = '1480885914:AAHv1aSiC5uym8PKUzsxBH_OVlMcdUm-9wo'
SECRET = 'b6c31fc9-6536-40a8-b8f2-7fb0cfccf164'
URL = 'https://api.telegram.org/bot' + API_TOKEN

payload = {
        'url': f'https://109.196.164.34/{SECRET}',
        # 'certificate': open("webhook_cert.pem", 'r'),
            }
# r = requests.post(URL + '/getWebhookInfo')
q = f'{URL}/setWebhook'
print(q)
r = requests.post(URL + '/setWebhook', data=payload, files={'certificate': open('webhook_cert.pem', 'r')})
print(r.text)



"""
import requests
url = "https://api.telegram.org/bot1480885914:AAHv1aSiC5uym8PKUzsxBH_OVlMcdUm-9wo/setWebhook"
data = {'url': "https://109.196.164.34/b6c31fc9-6536-40a8-b8f2-7fb0cfccf164"}
cert = open('/etc/ssl/certs/nginx-selfsigned.crt', 'r')
r = requests.post(url, data=data, files={'certificate': cert})
r.text
'{"ok":true,"result":true,"description":"Webhook was set"}'
"""
