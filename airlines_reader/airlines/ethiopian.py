
import requests
import logging

from requests import HTTPError

_LOG = logging.getLogger(__name__)

_URL = "https://dxbooking.ethiopianairlines.com/api/graphql"

_HEADERS = {
    'Host': 'dxbooking.ethiopianairlines.com',
    'Content-Length': '504',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Authorization': 'Bearer Basic anNvbl91c2VyOmpzb25fcGFzc3dvcmQ=',
    'Execution': '',
    'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"', 'Sec-Ch-Ua-Mobile': '?0',
    'Adrum': 'isAjax:true',
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'Dc-Url': '',
    'Application-Id': 'SWS1:SBR-DigConShpBk:fd34efe9a9',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Ssgtoken': 'undefined',
    'X-Sabre-Storefront': 'ETDX',
    'Ssotoken': 'undefined',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36',
    'Conversation-Id': 'undefined',
    'Origin': 'https://dxbooking.ethiopianairlines.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://dxbooking.ethiopianairlines.com/dx/ETDX/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Priority': 'u=1, i',
    'Connection': 'keep-alive'
}


def _payload(pnr, last_name):
    return {
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

def booking_details(pnr, last_name):
    _LOG.info(f"Retrieving booking details for pnr={pnr} last_name={last_name}")
    response = requests.post(_URL, json=_payload(pnr, last_name), headers=_HEADERS)
    _LOG.debug(f"Received response: " + str(response))
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    json_resp = response.json()
    if json_resp.get('data', {}).get('getMYBTripDetails'):
        return json_resp
    error_details = json_resp.get('extensions', {}).get('errors')
    _LOG.error(f"Received error for pnr={pnr}; last_name={last_name}; error_details={error_details}")
    raise HTTPError(error_details)
