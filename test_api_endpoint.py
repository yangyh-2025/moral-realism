import requests
import json

response = requests.get("http://localhost:8000/api/v1/simulation/46/round/1")
print(f"Status code: {response.status_code}")
data = response.json()
print(f"Total actions: {data.get('total_actions')}")
print(f"Actions list length: {len(data.get('actions', []))}")
print(f"First action: {data.get('actions', [{}])[0] if data.get('actions') else 'None'}")
