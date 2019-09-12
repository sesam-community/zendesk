import requests
import cherrypy
import json
from flask import Flask
from requests.exceptions import Timeout
from sesamutils import sesam_logger, VariablesConfig
import sys

app = app = Flask(__name__)

required_env_vars = ["user", "token"]
optional_env_vars = [("LOG_LEVEL", "DEBUG")] # Default values can be given to optional environment variables by the use of tuples

config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)

logger = sesam_logger('ZenDesk')
if not config.validate():
    sys.exit(1)


@app.route('/', methods=['GET'])
def get_tickets():
    try:
        with requests.Session() as session:
            session.auth = (config.user+'/token', config.token)
            logger.debug(f"we are inside the function.")
            response = session.get(url='https://sesamio.zendesk.com/api/v2/tickets.json', timeout=180)
            if response.ok:
                data = response.json()['tickets']
                logger.debug(json.dumps(data))
        return json.dumps(data)
    except Timeout as e:
        logger.error(f"Timeout issue while fetching tickets {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching tickets{e}")
    except Exception as e:
        logger.error(f"Issue while fetching tickets from Zendesk {e}")


if __name__ == '__main__':
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