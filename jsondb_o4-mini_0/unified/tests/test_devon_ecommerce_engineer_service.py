import os
import json
import time
import pytest
from devon_ecommerce_engineer.service import ProductService, app, service as default_service

@pytest.fixture
def sp(tmp_path):
    data_file = tmp_path / "data.json"
    version_dir = tmp_path / "versions"
    journal_file = tmp_path / "wal.log"
    ps = ProductService(data_file=str(data_file), version_dir=str(version_dir), journal_file=str(journal_file), encryption_key=b'0'*32)
    return ps

def test_create_read_update_delete(sp):
    prod = {'id':'p1','name':'Test','sku':'abc123','price':100,'stock':10}
    sp.create_product(prod.copy())
    data = sp.read_product('p1')
    assert data['name']=='Test'
    assert data['sku']=='ABC123'
    sp.update_product('p1',{'price':120,'stock':5})
    data2 = sp.read_product('p1')
    assert data2['price']==120
    assert data2['stock']==5
    sp.delete_product('p1')
    assert sp.read_product('p1') is None
    sp.undelete_product('p1', within_seconds=10)
    data3 = sp.read_product('p1')
    assert data3 is not None
    purged = sp.purge_deleted(0)
    assert purged == []
    sp.delete_product('p1')
    time.sleep(0.01)
    purged = sp.purge_deleted(0)
    assert 'p1' in purged
    assert sp.read_product('p1') is None

def test_batch_upsert_and_versions(sp):
    prods = [{'id':'a','name':'A','sku':'x','price':1,'stock':1},
             {'id':'b','name':'B','sku':'y','price':2,'stock':2}]
    sp.batch_upsert(prods)
    assert sp.read_product('a')['name']=='A'
    assert sp.read_product('b')['sku']=='Y'
    vs_a = sp.get_versions('a')
    assert len(vs_a)==1
    sp.update_product('a',{'price':5})
    vs_a2 = sp.get_versions('a')
    assert len(vs_a2)==2
    ts_files = [f for f in os.listdir(sp.version_dir) if f.startswith('a_')]
    ts = ts_files[0].split('_')[1].split('.')[0]
    orig = sp.rollback('a', ts)
    assert orig['price']==1

def test_encryption_at_rest(sp):
    sp.create_product({'id':'e','name':'E','sku':'k','price':1,'stock':1})
    content = open(sp.data_file,'rb').read()
    with pytest.raises(json.JSONDecodeError):
        json.loads(content.decode())
    raw = sp._decrypt(content)
    j = json.loads(raw.decode())
    assert 'e' in j

def test_journal(sp):
    sp.create_product({'id':'j','name':'J','sku':'j','price':1,'stock':1})
    sp.update_product('j',{'price':2})
    sp.delete_product('j')
    lines = open(sp.journal_file).read().strip().splitlines()
    assert len(lines)==3
    entries = [json.loads(l) for l in lines]
    ops = [e['operation'] for e in entries]
    assert ops==['create','update','delete']

def test_api_endpoints(tmp_path):
    df = tmp_path / "data.json"
    vd = tmp_path / "versions"
    jl = tmp_path / "wal.log"
    app.testing = True
    default_service.__init__(data_file=str(df), version_dir=str(vd), journal_file=str(jl), encryption_key=b'1'*32)
    client = app.test_client()
    rv = client.post('/products', json={'id':'z','name':'Z','sku':'z','price':10,'stock':5})
    assert rv.status_code==201
    j = rv.get_json()
    assert j['sku']=='Z'
    rv = client.get('/products/z')
    assert rv.status_code==200
    rv = client.patch('/products/z', json={'price':20})
    assert rv.get_json()['price']==20
    rv = client.delete('/products/z')
    assert rv.status_code==204
    rv = client.get('/products/z')
    assert rv.status_code==404
    rv = client.post('/products/z/undelete')
    assert rv.status_code==204
    rv = client.get('/products/z')
    assert rv.status_code==200
    rv = client.post('/batch_upsert', json=[{'id':'x','name':'X','sku':'x','price':1,'stock':1}])
    assert rv.status_code==204
    rv = client.get('/versions/x')
    assert rv.status_code==200
    assert isinstance(rv.get_json(), list)
    rv = client.post('/rollback/x/0000')
    assert rv.status_code==404
    rv = client.get('/metrics')
    assert rv.status_code==200
    rv = client.get('/health')
    assert rv.status_code==200 and rv.get_json()['status']=='ok'
