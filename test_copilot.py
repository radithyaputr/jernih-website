import requests
import json

url = "http://localhost:8000/api/copilot/chat"
data = {"message": "Halo saya butuh bantuan pendidikan"}

print("Calling API...")
response = requests.post(url, json=data)
print(f"Status code: {response.status_code}")
print("Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
