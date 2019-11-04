import requests
import cherrypy
import json
import logging
from flask import Flask, request, Response
from requests.exceptions import Timeout
from sesamutils import VariablesConfig
import paste.translogger
import urllib.parse
from dateutil.parser import parse

import sys
import os

app = app = Flask(__name__)

logger = logging.getLogger("zendesk-service")

# Default
required_env_vars = ["user", "token"]
optional_env_vars = [("LOG_LEVEL", "INFO")]
date_fields =["created_at","last_login_at","updated_at",""]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)


def stream_as_json(generator_function):
    """
    Stream list of objects as JSON array
    :param generator_function:
    :return:
    """
    first = True

    yield '['

    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False

        yield json.dumps(item)

    yield ']'

def datetime_format(dt):
    return '%04d' % dt.year + dt.strftime("-%m-%dT%H:%M:%SZ")


def to_transit_datetime(dt_int):
    return "~t" + datetime_format(dt_int)

@app.route('/tickets')
def get_tickets():
    try:
        if request.args.get('since') is None:
            unix_time_update_date = 1332034771  # Sunday, March 18, 2012 2:39:31 AM Starting from beginning :-)
            logger.debug(f"since value set from ms: {unix_time_update_date}")
        else:
            unix_time_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {unix_time_update_date}")

        return Response(stream_as_json(GetTickets(unix_time_update_date)), mimetype='application/json')

    except Timeout as e:
        logger.error(f"Timeout issue while fetching tickets {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching tickets{e}")
    except Exception as e:
        logger.error(f"Issue while fetching tickets from Zendesk {e}")


def GetTickets(unix_time_update_date):
    check_items = True
    ticket_list = list()
    result = list()
    url = f'https://sesam.zendesk.com/api/v2/incremental/tickets.json?start_time={unix_time_update_date}'
    while check_items:
        response = requests.get(url, auth=(config.user + '/token', config.token))
        data = response.json()
        if "next_page" in data:
            url = data['next_page']

        for item in data['tickets']:
            i = dict(item)
            for f in i:
                if f in date_fields and i[f]:
                    i[f] = to_transit_datetime(parse(i[f]))
            i["_id"] = str(item['id'])
            i["_updated"] = str(i['generated_timestamp'])
            yield i

        if data['count'] < 1000:  # pagination used for Zendesk incremental importing
            check_items = False


@app.route('/items/<items>')
def get_items(items):
    try:
        return Response(stream_as_json(GetData(items, request.args.get('since'))), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching {items} {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching {items}{e}")
    except Exception as e:
        logger.error(f"Issue while fetching {items} from Zendesk {e}")


def GetData(items, since):
    url = f'https://sesam.zendesk.com/api/v2/{items}.json?limit=1000'

    if since:
        url += f"&cursor={urllib.parse.quote(since)}"

    updated = ""

    while url:
        logger.info(f"Get data using: {url}")
        response = requests.get(url, auth=(config.user + '/token', config.token))
        if response.ok:
            data = response.json()
            logger.debug(f"Got data: {data}")
            if len(data) == 0:
                break
            count = 0
            if updated == "" and "after_cursor" in data:
                updated = data["after_cursor"]
            if since and "after_url" in data:
                url = data["after_url"]
            elif  "before_url" in data:
                url = data["before_url"]
            elif  "next_page" in data:
                url = data["next_page"]

            for x in data:
                logger.debug(f"Field: {data[x]} - type {type(data[x])}")
                if type(data[x]) is list:
                    for item in data[x]:
                        i = dict(item)
                        for f in i:
                            if f in date_fields and i[f]:
                                i[f] = to_transit_datetime(parse(i[f]))
                        i["_id"] = str(item['id'])
                        i["_updated"] = updated
                        yield i
                        count += 1

            logger.info(f'Yielded: {count}')
        else:
            raise ValueError(f'value object expected in response to url: {url} got {response}')
            break



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

    logger.info(f"Config: {config.user} - {config.token}")

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()