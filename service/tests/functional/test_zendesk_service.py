import requests
import json

#TODO
# Requiers more thinking about how to do mocking of zendesk

# def test_new_ticket():
#     """
#     GIVEN a response
#     WHEN endpoint /transform/ticket/new get a call
#     THEN check response value relativ to call method and payload
#     """
#     payload = [{"ticket": {"id": "test_id","subject": "My printer is on fire!", "comment": { "body": "The smoke is very colorful." }}}]
#     rv = requests.post('http://zendesk-service:5000/transform/ticket/new',json=payload)
#     echo = rv.json()
#     assert isinstance(echo,list)
#     echo = echo[0]
#     echo_payload = echo['payload']
#     assert isinstance(echo_payload,dict)
#     assert echo_payload["ticket"]['comment']['body'] == payload[0]["ticket"]['comment']['body']
#     assert echo['content_type'] == 'application/json'

# def test_update_ticket():
#     """
#     GIVEN a response
#     WHEN endpoint /transform/ticket/update get a call
#     THEN check response value relativ to call method and payload
#     """
#     payload = [{"ticket": {"id": "test_id","subject": "My printer is on fire!", "comment": { "body": "The smoke is very colorful." }}}]
#     rv = requests.post('http://zendesk-service:5000/transform/ticket/update',json=payload)
#     echo = rv.json()
#     assert isinstance(echo,list)
#     echo = echo[0]
#     echo_payload = echo['payload']
#     assert isinstance(echo_payload,dict)
#     assert echo_payload["ticket"]['comment']['body'] == payload[0]["ticket"]['comment']['body']
#     assert echo['content_type'] == 'application/json'


