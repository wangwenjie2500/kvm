# -*- coding:utf-8 -*-
from flask import Flask
import web_api_module
import json

app = Flask(__name__, static_url_path='')
#
@app.route('/api/v0.1/host/control/<tuple>',methods=['GET'])
def hostControl(tuple):
    if not tuple:
        return {"Error":"451"}
    f = web_api_module.host().hostRegister(tuple)
    return json.dumps(f)

@app.route('/api/v0.1/cluster/select/<tuple>',methods=['GET'])
def hostSelect(tuple):
    if not tuple:
        return {"Error": "451"}
    f = web_api_module.host().hostSelect(tuple)
    return json.dumps(f)


@app.route('/api/v0.1/cluster/flush/<tuple>',methods=['GET'])
def domainFlush(tuple):
    if not tuple:
        return {"Error": "451"}
    f = web_api_module.domain().domainFlush(tuple)
    return json.dumps(f)

@app.route('/api/v0.1/disk/select/<tuple>',methods=['GET'])
def diskSelect(tuple):
    if not tuple:
        return {"Error" : "451"}
    f = web_api_module.disk().diskControl(tuple)
    return json.dumps(f)
@app.route('/api/v0.1/disk/crontrol/<tuple>',methods=['GET'])
def diskControl(tuple):
    if not tuple:
        return {"Error" : "451"}
    f = web_api_module.disk().diskControl(tuple)
    return json.dumps(f)


@app.route('/api/v0.1/domain/select/<tuple>',methods=['GET'])
def domainSelect(tuple):
    if not tuple:
        return {'Error' : "451"}
    f = web_api_module.domain().domainControl(tuple=tuple)
    return json.dumps(f)


@app.route('/api/v0.1/domain/crontrol/<tuple>',methods=['GET'])
def domainCrontol(tuple):
    if not tuple:
        return {'Error':"451"}
    f = web_api_module.domain().domainCrontolInfo(tuple=tuple)
    return json.dumps(f)

@app.route('/api/v0.1/image/select/<tuple>',methods=['GET'])
def iamgeSelect(tuple):
    if not tuple:
        return {'Error' : "451"}
    f = web_api_module.image().imageControl(tuple=tuple)

    return json.dumps(f)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8085)