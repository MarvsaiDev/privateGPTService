from datetime import datetime

import requests

url = 'http://localhost:8000/ingest/'  # Replace with your actual URL

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

# Assuming you have a dictionary named `data` with the text to submit
data = {
    'text': 'My ACC Order ACC-12423424',
    'filname': 'testFile2',
    'datestr': datetime.now().isoformat(),
    'jobid': 'testjob'
}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    print("Text submitted successfully.")
else:
    print(f"Error submitting text. Status code: {response.status_code}")
    print(response.text)