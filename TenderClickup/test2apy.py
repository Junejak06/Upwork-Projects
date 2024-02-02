import requests
import pandas as pd

# ClickUp API Key
api_key = "pk_3817504_QSW6U89PBX3VKOZGGTZN0FMOR237UR06"
space_id = "90100456353"
list_id = "901002697169"
url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

headers = {"Authorization": api_key}
excel_file_path = "/Users/kunaljuneja/Upwork/TenderClickup/Municipal Corporation of Greater Mumbai.csv"
df = pd.read_csv(excel_file_path)

# Fetching the first row
row = df.iloc[0]

data = {
    "name": "XYZ",  # Assuming you still want to use the title for the task's name
    "custom_fields": [
        {
            "name": "Organisation Chain",
            "value": row['organisation_chain']
        }
    ]
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("Successfully added 'Organization Chain' value!")
else:
    print(f"Failed with status code {response.status_code}. Response: {response.text}")
