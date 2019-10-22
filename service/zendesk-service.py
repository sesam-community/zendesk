import requests
import cherrypy
import json
import logging
from flask import Flask, request, Response, abort
from requests.exceptions import Timeout
from sesamutils import VariablesConfig
import paste.translogger


import sys
import os

app = app = Flask(__name__)

logger = logging.getLogger("zendesk-service")

# Default
required_env_vars = ["user", "token","zendeskSubdomain"]
optional_env_vars = [("LOG_LEVEL", "INFO","ZENDESK_API_ROOT")] 
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)

if not hasattr(config,"ZENDESK_API_ROOT"):
    setattr(config,'ZENDESK_API_ROOT', 'zendesk.com/api/v2/')


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
            session.auth = (config.user+'/token', config.token)
            check_items = True
            ticket_list = list()
            url = f'https://{config.zendeskSubdomain}.{config.ZENDESK_API_ROOT}incremental/tickets.json?start_time={unix_time_update_date}'
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

@app.route('/ticket/update/<ticketID>') 
def update_ticket(ticketID):
    try:
        if request.method != "PUT":
            abort(405)
        with requests.Session() as session:
            session.auth = (config.user+'/token', config.token)
            url = f'https://{config.zendeskSubdomain}.{config.ZENDESK_API_ROOT}tickets/{ticketID}.json' 
            response = session.put(url, data=request.get_data(), timeout=180)
            return Response(response.content, mimetype=response.content_type)
    except Timeout as e:
        logger.error(f"Timeout issue while fetching tickets {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching tickets{e}")
    except Exception as e:
        logger.error(f"Issue while fetching tickets from Zendesk {e}")


@app.route('/items/<items>')
def get_items(items):
    try:
        with requests.Session() as session:
            session.auth = (config.user+'/token', config.token)
            url = f'https://{zendeskSubdomain}.{config.ZENDESK_API_ROOT}{items}.json'
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


if __name__ == '__main__':
    format_string = '%(name)s - %(levelname)s - %(message)s'
    # Log to stdout, change to or add a (Rotating)FileHandler to log to a file
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    # Comment these two lines if you don't want access request logging
    app.wsgi_app = paste.translogger.TransLogger(app.wsgi_app, logger_name=logger.name,
                                                 setup_console_handler=False)
    app.logger.addHandler(stdout_handler)

    logger.propagate = False
    log_level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))  # default log level = INFO
    logger.setLevel(level=log_level)
    cherrypy.tree.graft(app, '/')
    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        'environment': 'production',
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()