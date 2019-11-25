import os
from datetime import datetime

import json

from flask import Flask, request, jsonify, Response, abort

import requests
from requests.exceptions import Timeout

from sesamutils import sesam_logger, VariablesConfig
from sesamutils.flask import serve

from collections import OrderedDict

app = Flask(__name__)
logger = sesam_logger('zendesk-service', app=app, timestamp=True)

# Default values can be given to optional environment variables by the use of tuples
required_env_vars = ["USER", "TOKEN","SUBDOMAIN"]
optional_env_vars = [("DEBUG","false"),("LOG_LEVEL", "INFO"),"DUMMY_URL"] 
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
    
if not config.validate():
    logger.error("Environment variables do not validate. Exiting system.")
    os.sys.exit(1)

USER = config.USER
TOKEN = config.TOKEN
SUBDOMAIN = config.SUBDOMAIN

DEBUG = config.DEBUG in ["true","True","yes"]

if hasattr(config, 'DUMMY_URL'):
    ZENURL = config.DUMMY_URL
    if (ZENURL[-1] == '/'): 
        ZENURL = ZENURL[:-1]
    logger.info(f"Using DUMMY_URL {ZENURL} for Zendesk-api-base-url")
else: 
    ZENURL = f'https://{SUBDOMAIN}.zendesk.com/api/v2'
    logger.info("Using {ZENURL} for Zendesk-api-base-url") 

@app.route('/tickets') 
def get_tickets():
    try:
        if request.args.get('since') is None:
            unix_time_update_date = 1332034771  # Sunday, March 18, 2012 2:39:31 AM Starting from beginning :-)
            logger.debug(f"since value set from ms: {unix_time_update_date}")
        else:
            unix_time_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {unix_time_update_date}")
        with requests.Session() as session:
            session.auth = (USER+'/token', TOKEN)
            check_items = True
            ticket_list = list()
            url = f'{ZENURL}/incremental/tickets.json?start_time={unix_time_update_date}'
            while check_items:
                response = session.get(url, timeout=180)
                data = response.json()
                ticket_list = ticket_list + data['tickets']
                url = data['next_page']
                if data['count'] < 1000:  # pagination used for Zendesk incremental importing
                    check_items = False
            result = [dict(item, _updated=data['end_time'], _id=str(item['id'])) for item in
                      ticket_list]
            return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching tickets {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching tickets{e}")
    except Exception as e:
        logger.error(f"Issue while fetching tickets from Zendesk {e}")

@app.route('/transform/update/ticket/<ticketID>',methods=['POST']) 
def update_ticket(ticketID):
    try:
        with requests.Session() as session:
            session.auth = (USER+'/token', TOKEN)
            url = f'{ZENURL}/tickets/{ticketID}.json' 
            if DEBUG: logger.debug("Input payload: "+str(request.get_json()))
            response = session.put(url, json=request.get_json(), timeout=180)
            if DEBUG: logger.debug("Output payload: "+str(response.json()))
            return jsonify(response.json())
    except Timeout as e:
        logger.error(f"Timeout issue while updating ticket {ticketID}: {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while updating ticket {ticketID}: {e}")
    except Exception as e:
        logger.error(f"Issue while updating ticket {ticketID} from Zendesk: {e}")


@app.route('/items/<path:items>')
def get_items(items):
    try:
        with requests.Session() as session:
            session.auth = (USER+'/token', TOKEN)
            url = f'{ZENURL}/{items}.json'
            response = session.get(url, timeout=180)
            data = response.json()
            result = list()
            if data is not None:
                data = data[items]
                result = [dict(item, _id=str(item['id'])) for item in data]
            return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching {items} {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching {items}{e}")
    except Exception as e:
        logger.error(f"Issue while fetching {items} from Zendesk {e}")


if __name__ == "__main__":
    serve(app)