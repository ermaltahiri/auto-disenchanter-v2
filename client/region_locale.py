def get_region_locale(connection):
    return connection.get('/riotclient/region-locale').json()
