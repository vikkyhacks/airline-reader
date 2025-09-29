import requests
import logging
import config
from requests import HTTPError
from airlines_reader.utils.cache import file_cache

_LOG = logging.getLogger(__name__)
_LOG.setLevel(config.HTTP_LOG_LEVEL)  # Ensure high verbosity

_URL = "https://dxbooking.ethiopianairlines.com/api/graphql"

_HEADERS = {
    'Host': 'dxbooking.ethiopianairlines.com',
    'Content-Length': '504',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Authorization': 'Bearer Basic anNvbl91c2VyOmpzb25fcGFzc3dvcmQ=',
    'Execution': '',
    'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
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


def _log_request(prepared):
    """Logs the full HTTP request."""
    _LOG.debug("----- HTTP Request -----")
    _LOG.debug(f"{prepared.method} {prepared.url}")
    for k, v in prepared.headers.items():
        _LOG.debug(f"{k}: {v}")
    if prepared.body:
        try:
            _LOG.debug("Body:\n%s", prepared.body.decode() if isinstance(prepared.body, bytes) else prepared.body)
        except Exception:
            _LOG.debug("Body: <non-decodable binary>")
    _LOG.debug("------------------------")


def _log_response(response):
    """Logs the full HTTP response."""
    _LOG.debug("----- HTTP Response -----")
    _LOG.debug(f"Status: {response.status_code} {response.reason}")
    for k, v in response.headers.items():
        _LOG.debug(f"{k}: {v}")
    try:
        _LOG.debug("Body:\n%s", response.text)
    except Exception:
        _LOG.debug("Body: <non-decodable>")
    _LOG.debug("-------------------------")
    return response


# @file_cache()
def booking_details(pnr, last_name):
    _LOG.info(f"Retrieving booking details for pnr={pnr} last_name={last_name}")
    headers = config.HEADERS | _HEADERS

    session = requests.Session()
    session.trust_env = False
    session.proxies = {
        "http": "http://localhost:8080",
        "https": "https://localhost:8080",  # Burp listens as HTTP proxy for both
    }
    session.verify = False
    request = requests.Request("POST", _URL, json=_payload(pnr, last_name), headers=headers)
    prepared = session.prepare_request(request)

    _log_request(prepared)

    response = session.send(prepared, timeout=30)
    
    _log_response(response)

    _LOG.info(f"Received response for pnr={pnr} last_name={last_name}: {response}")
    response.raise_for_status()

    json_resp = response.json()
    _LOG.info("Response data: %s", json_resp)

    if json_resp.get('data', {}).get('getMYBTripDetails'):
        return json_resp

    error_details = json_resp.get('extensions', {}).get('errors')
    _LOG.error(f"Received error for pnr={pnr}; last_name={last_name}; error_details={error_details}")
    raise HTTPError(error_details)
