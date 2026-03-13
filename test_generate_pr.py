import requests

url = "http://127.0.0.1:8000/generate-pr-highest-risk"

response = requests.post(url)

print("Status Code:", response.status_code)
print("Raw Response:")
print(response.text)