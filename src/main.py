import json

import json2html

from src.airlines.ethiopian import make_graphql_post_request
from src.airlines.model import AirlineModelBuilder

if __name__ == '__main__':
    inputs = [
        {"pnr": "WHPSPL", "last_name": "GOTO"},
        {"pnr": "DNZGTN", "last_name": "HABTE"},
        {"pnr": "ATHXFL", "last_name": "HARRISON"},
        {"pnr": "KWDGQL", "last_name": "HENRY"}
    ]
    for ip in inputs:
        print("[+] Processing " + str(ip))
        gql_resp = make_graphql_post_request(**ip)
        with open(f"./dump/{ip['pnr']}_{ip['last_name']}_original.html", "w") as fp:
            fp.write(json2html.json2html.convert(json=json.dumps(gql_resp)))
        if not gql_resp:
            continue
        builder = AirlineModelBuilder(gql_resp)
        model = builder.build()
        with open(f"./dump/{ip['pnr']}_{ip['last_name']}_trimmed.html", "w") as fp:
            fp.write(json2html.json2html.convert(json=json.dumps(model.__dict__)))
