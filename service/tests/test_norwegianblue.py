
def test_get_routes(client):
    """
    GIVEN a response
    WHEN endpoint /api/orders get a GET call
    THEN check response value
    """
    rv = client.get('/api/orders')
    assert rv.status_code == 200
    assert rv.json[0]['path'] == 'api/orders'
    assert rv.json[0]['http_method'] == 'GET'

def test_put_routes(client):
    """
    GIVEN a response
    WHEN endpoint /api/orders/update/<int:orderID> get a call
    THEN check response value relativ to orderID and call method
    """
    rv = client.put('/api/orders/update/2')
    assert rv.status_code == 200
    assert rv.json[0]['path'] == 'api/orders/update/2'
    assert rv.json[0]['http_method'] == 'PUT'

def test_generic_routes(client):
    """
    GIVEN a response
    WHEN endpoint /api/orders/generic/<path:txt> get a call
    THEN check response value relativ to txt and call method
    """
    rv = client.get('/api/generic/test/1')
    assert rv.status_code == 200
    assert rv.json[0]['path'] == 'api/generic/test/1'

