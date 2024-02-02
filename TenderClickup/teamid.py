import requests

api_key = "pk_3817504_QSW6U89PBX3VKOZGGTZN0FMOR237UR06"

url = "https://api.clickup.com/api/v2/team"

headers = {"Authorization": api_key}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Failed with status code {response.status_code}. Response: {response.text}")
