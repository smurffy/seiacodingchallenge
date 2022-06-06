import sys
import sys
sys.path.append('..') # TODO: more elegant pkg solution
from run import create_app

def test_config():
    assert not create_app().testing
    assert create_app({
        'TESTING': True,
        'DEBUG': True,
        'FLASK_ENV' : 'development'
    }).testing


def test_post_temp(client):
    response = client.post('/temp', json={"data": "365951380:1640995229697:'Temperature':58.48256793121914"})
    print(response.json)
    assert response.status_code == 200
    assert not response.json.get("overtemp")
    response = client.post('/temp', json={"data": "365951380:1640995229697:'Temperature':98.48256793121914"})
    assert response.status_code == 200
    assert response.json.get("overtemp")


def test_get_errors(client):
    response = client.get('/errors')
    assert response.status_code == 200
    assert "errors" in response.json.keys()


def test_put_errors(client):
    response = client.put("/errors/abc:16409952296:'Temp':Sixty")
    assert response.status_code == 200
    assert response.json.get("error")


def test_delete_errors(client):
    response = client.delete('/errors')
    assert response.status_code in (204, 400)
