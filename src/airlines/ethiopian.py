
import requests
import json


def make_graphql_post_request(pnr, last_name):
    url = "https://dxbooking.ethiopianairlines.com/api/graphql"
    payload = {
        "operationName": "getMYBTripDetails",
        "variables": {
            "pnrQuery": {
                "pnr": pnr,
                "lastName": last_name
            }
        },
        "extensions": {},
        "query": """
        query getMYBTripDetails($pnrQuery: JSONObject!) {
          getMYBTripDetails(pnrQuery: $pnrQuery) {
            originalResponse
          }
        }
        """
    }

    headers = {'Host': 'dxbooking.ethiopianairlines.com', 'Content-Length': '504', 'Sec-Ch-Ua-Platform': '"macOS"',
               'Authorization': 'Bearer Basic anNvbl91c2VyOmpzb25fcGFzc3dvcmQ=', 'Execution': '',
               'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"', 'Sec-Ch-Ua-Mobile': '?0',
               'Adrum': 'isAjax:true',
               'Accept': '*/*', 'Content-Type': 'application/json', 'Dc-Url': '',
               'Application-Id': 'SWS1:SBR-DigConShpBk:fd34efe9a9', 'Accept-Language': 'en-GB,en;q=0.9',
               'Ssgtoken': 'undefined',
               'X-Sabre-Storefront': 'ETDX', 'Ssotoken': 'undefined',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36',
               'Conversation-Id': 'undefined', 'Origin': 'https://dxbooking.ethiopianairlines.com',
               'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
               'Referer': 'https://dxbooking.ethiopianairlines.com/dx/ETDX/', 'Accept-Encoding': 'gzip, deflate, br',
               'Priority': 'u=1, i', 'Connection': 'keep-alive'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_resp = response.json()
        if json_resp.get('data', {}).get('getMYBTripDetails'):
            return json_resp
        error_details = json_resp.get('extensions', {}).get('errors')
        print(f"Received error for pnr={pnr}; last_name={last_name}; error_details={error_details}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error making GraphQL request: {e}")
        if response is not None:
            print(f"Response code: {response.status_code}")
            try:
                print(response.json())  # Attempt to print the json of the response, even if it is an error.
            except json.JSONDecodeError:
                print(response.text)  # If the response is not json, print the text.
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding json: {e}")
        if response is not None:
            print(f"Response code: {response.status_code}")
            print(response.text)  # Print the text if the json can't be decoded.
        return None

# response_data = make_graphql_post_request('HEEPIS', 'ASAMOAH')
#
# if response_data:
#     print(response_data)
#     print(json2html.json2html.convert(json=response_data))
#
