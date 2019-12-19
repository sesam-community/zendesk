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
logger = sesam_logger('zendesk', app=app, timestamp=True)

# Default values can be given to optional environment variables by the use of tuples
required_env_vars = ["USER", "TOKEN","SUBDOMAIN"]
optional_env_vars = [("DEBUG","false"),("LOG_LEVEL", "INFO"),"DUMMY_URL"] 
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
    
if not config.validate():
    logger.error("Environment variables do not validate. Exiting system.")
    os.sys.exit(1)

USER = config.USER
TOKEN = config.TOKEN
ZEN_AUTH = (USER+'/token', TOKEN)
SUBDOMAIN = config.SUBDOMAIN
DUMMY_URL = False

DEBUG = config.DEBUG in ["true","True","yes"]

if hasattr(config, 'DUMMY_URL'):
    DUMMY_URL = config.DUMMY_URL 
    ZENURL = DUMMY_URL
    if (ZENURL[-1] == '/'): 
        ZENURL = ZENURL[:-1]
    logger.info(f"Using DUMMY_URL {ZENURL} for Zendesk-api-base-url")
else: 
    ZENURL = f'https://{SUBDOMAIN}.zendesk.com/api/v2'
    logger.info(f"Using {ZENURL} for Zendesk-api-base-url")

def stream_as_json(generator_function):
    """Helper generator to support streaming with flask"""
    first = True
    yield '['
    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(item)
    yield ']'

@app.route('/source/ticket/all',methods=["GET"]) 
def get_tickets():
    try:
        if request.args.get('since') is None:
            unix_time_update_date = 1332034771  # Sunday, March 18, 2012 2:39:31 AM Starting from beginning :-)
            logger.debug(f"since value set from ms: {unix_time_update_date}")
        else:
            unix_time_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {unix_time_update_date}")
        with requests.Session() as session:
            session.auth = ZEN_AUTH
            return Response(stream_as_json(get_items(session,unix_time_update_date)), mimetype='application/json; charset=utf-8') #Rewrite to use stream_as_json
            # return Response(stream_as_json(get_page(url)), mimetype=‘application/json’)
    except Timeout as e:
        logger.error(f"Timeout issue while fetching tickets {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching tickets{e}")
    except Exception as e:
        logger.error(f"Issue while fetching tickets from Zendesk {e}")

@app.route('/transform/ticket/update/',methods=['POST']) 
def update_ticket():
    if request.is_json:
        ticket_list = request.get_json()
        logger.debug(type(ticket_list))
    else:
        logger.error('Content type must be json and not:'+str(request.content_type))
        abort(415)
    ticket_data = ticket_list[0] # only support single element
    if 'ticket' in ticket_data.keys() and 'id' in ticket_data['ticket'].keys():
        id = ticket_data['ticket'].pop('id')
        ticket = {"ticket": ticket_data['ticket']}
    else:
        logger.error('Paylod not in correct format. id is mandatory to update.')
        abort(400)
    try:
        with requests.Session() as session:
            session.auth = ZEN_AUTH
            url = f'{ZENURL}/tickets/{id}.json'
            # https://developer.zendesk.com/rest_api/docs/support/tickets#update-ticket
            if DEBUG: logger.debug("Input payload: "+str(ticket))
            response = session.put(url, json=ticket, timeout=180)
            result = response.json()
            if DEBUG: logger.debug("Output payload: "+str(result))
            # Status should be 201 Created
            logger.info("Statuscode from Zendesk: "+str(response.status_code))
            #insert id for Sesam
            if isinstance(result,dict):
                result = [result]
            result[0]['_id'] = result[0]['ticket']["id"]
            return Response(json.dumps(result), mimetype='application/json; charset=utf-8') 
    except Timeout as e:
        logger.error(f"Timeout issue while updating ticket {ticketID}: {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while updating ticket {ticketID}: {e}")
    except Exception as e:
        logger.error(f"Issue while updating ticket {ticketID} from Zendesk: {e}")

@app.route('/transform/ticket/new/',methods=['POST']) 
def new_ticket():
    if request.is_json:
        ticket_list = request.get_json()
        logger.debug(type(ticket_list))
    else:
        logger.error('Content type must be json and not:'+str(request.content_type))
        abort(415)
    ticket_data = ticket_list[0] # Debug/testing single element
    if 'ticket' in ticket_data.keys() and 'comment' in ticket_data['ticket'].keys():
        ticket = {"ticket": ticket_data['ticket']}
    else:
        logger.error('Paylod not in correct format. Comment is mandatory.')
        abort(400)
    try:
        with requests.Session() as session:
            session.auth = ZEN_AUTH
            url = f'{ZENURL}/tickets.json'
            # https://developer.zendesk.com/rest_api/docs/support/tickets#create-ticket
            if DEBUG: logger.debug("Input payload: "+str(ticket))
            response = session.post(url, json=ticket, timeout=180)
            result = response.json()
            if DEBUG: logger.debug("Output payload: "+str(result))
            logger.info("Statuscode from Zendesk (should be 201 Created): "+str(response.status_code))
            #insert id for Sesam
            result['_id'] = result["ticket"]['id']
            if isinstance(result,dict):
                result = [result]
            result[0]['_id'] = result[0]['ticket']["id"]
            return Response(json.dumps(result), mimetype='application/json; charset=utf-8') 
    except Timeout as e:
        logger.error(f"Timeout issue while updating ticket {ticketID}: {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while updating ticket {ticketID}: {e}")
    except Exception as e:
        logger.error(f"Issue while updating ticket {ticketID} from Zendesk: {e}")


def get_items(session,unix_time_update_date):
    """Helper generator to support streaming with flask"""
    url = f'{ZENURL}/incremental/tickets.json?start_time={unix_time_update_date}'
        # https://developer.zendesk.com/rest_api/docs/support/tickets#list-tickets
    check_items = True
    while check_items:
        response = session.get(url, timeout=180)
        data = response.json()
        end_time = data["end_time"]
        url = data['next_page']
        logger.debug(f"Next page url: {url}")
        # logger.debug(f"Data count: {data['count']}")
        for item in data['tickets']:
            logger.debug(f"item: {item}")
            item["_id"] = str(item["id"])
            item["_updated"] = end_time
            yield item
        if data['count'] < 1000:  # pagination used for Zendesk incremental importing. Next page will newer be none when using timestamp 
            check_items = False

if __name__ == "__main__":
    serve(app)