import requests
import json

data = open('input.json').read()

headers = {'content-type': 'application/json'}

r = requests.post("http://localhost/services/analyzeSubmission", data=data, headers=headers)

print r.text
