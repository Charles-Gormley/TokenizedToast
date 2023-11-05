import requests

def refresh_access_token(client_id, client_secret, refresh_token):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    r = requests.post('https://oauth2.googleapis.com/token', data=payload)
    if r.status_code == 200:
        return r.json()['access_token']
    else:
        print('Failed to refresh access token:', r.text)
        return None