import requests
import pandas as pd

# ClickUp API Key
api_key = "pk_3817504_QSW6U89PBX3VKOZGGTZN0FMOR237UR06"
space_id = "90100456353"
list_id = "901002697169"
url = f"https://api.clickup.com/api/v2/list/{list_id}/field"
headers = {"Authorization": api_key}

# Function to get or create option UUID
def get_or_create_option_uuid(desired_value):
    response = requests.get(url, headers=headers)
    fields = response.json().get('custom_fields', [])

    # Find the 'Organisation Chain' field
    for field in fields:
        if field.get('name') == 'Organisation Chain':
            options = field.get('type_config', {}).get('options', [])

            # Check if the desired value already exists
            for option in options:
                if option.get('name') == desired_value:
                    return option.get('id')  # Return existing UUID

            # If not, create a new option
            new_option = {
                "name": desired_value
            }
            field['type_config']['options'].append(new_option)

            update_response = requests.put(url + f"/{field['id']}", json={"type_config": field['type_config']}, headers=headers)
            if update_response.status_code == 200:
                new_option_id = update_response.json().get('type_config', {}).get('options', [])[-1].get('id')
                return new_option_id  # Return UUID of the newly created option
    return None

excel_file_path = "/Users/kunaljuneja/Upwork/TenderClickup/Municipal Corporation of Greater Mumbai.csv"
df = pd.read_csv(excel_file_path)
row = df.iloc[0]

organization_chain_value = row['organisation_chain']
option_uuid = get_or_create_option_uuid(organization_chain_value)

data = {
    "name": "Default Task Name",
    "custom_fields": [
        {
            "id": "d6312fc4-b23f-4af0-809f-e463b26d6af8",  # This is the 'Organisation Chain' field ID
            "value": option_uuid
        }
    ]
}

response = requests.post(f"https://api.clickup.com/api/v2/list/{list_id}/task", json=data, headers=headers)

if response.status_code == 201:
    print("Successfully added 'Organization Chain' value!")
else:
    print(f"Failed with status code {response.status_code}. Response: {response.text}")