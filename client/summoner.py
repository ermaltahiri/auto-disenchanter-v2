import requests


def get_level(connection):
    try:
        res = connection.get('/lol-summoner/v1/current-summoner')
        res_json = res.json()
        return res_json['summonerLevel']
    except requests.exceptions.RequestException:
        return -1
