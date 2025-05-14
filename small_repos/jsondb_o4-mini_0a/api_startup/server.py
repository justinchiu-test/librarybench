from db_engine import DBEngine

def start_rest_server(host='127.0.0.1', port=5000, path='data/events.json', key=None):
    engine = DBEngine(path=path, encryption_key=key)
    engine.startRestServer(host=host, port=port)
