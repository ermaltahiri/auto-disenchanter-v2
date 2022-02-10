def get_blue_essence(connection):
    res = connection.get('/lol-store/v1/wallet')
    res_json = res.json()
    if 'ip' not in res_json:
        return -1
    return res_json['ip']
