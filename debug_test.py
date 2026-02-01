import urllib.request
import json
import datetime

url = 'http://localhost:5000/predict'
data = {
    'amount': 100,
    'merchant': 'test',
    'location': 'Kolkata',
    'date': '2026-01-31',
    'time': '12:00',
    'cardType': 'visa'
}

print(f"Testing URL: {url}")
print(f"Payload: {data}")

try:
    req = urllib.request.Request(url, json.dumps(data).encode('utf-8'), {'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as f:
        print("Success!")
        print(f.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(f"Error Body: {e.read().decode('utf-8')}")
