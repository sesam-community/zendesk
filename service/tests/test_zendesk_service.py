import requests

def test_new_ticket():
    """
    GIVEN a response
    WHEN endpoint /transform/ticket/new get a call
    THEN check response value relativ to call method and payload
    """
    payload = [{"ticket": {"subject": "My printer is on fire!", "comment": { "body": "The smoke is very colorful." }}}]
    rv = requests.post('http://zendesk-service:5000/transform/ticket/new',json=payload)
    assert isinstance(rv.json(),list)

