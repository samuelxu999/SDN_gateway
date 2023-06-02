import time
import sys
import json
import logging
from argparse import ArgumentParser

from flask import Flask, jsonify
from flask import abort,make_response,request

from utilities import TypesUtil,FileUtil
from RPC_Client import PRC_Client

app = Flask(__name__)

#========================================== Error handler ===============================================
#Error handler for abort(404) 
@app.errorhandler(404)
def not_found(error):
    #return make_response(jsonify({'error': 'Not found'}), 404)
    response = jsonify({'result': 'Failed', 'message':  error.description['message']})
    response.status_code = 404
    return response

#Error handler for abort(400) 
@app.errorhandler(400)
def type_error(error):
    #return make_response(jsonify({'error': 'type error'}), 400)
    response = jsonify({'result': 'Failed', 'message':  error.description['message']})
    response.status_code = 400
    return response
	
#Error handler for abort(401) 
@app.errorhandler(401)
def access_deny(error):
    response = jsonify({'result': 'Failed', 'message':  error.description['message']})
    response.status_code = 401
    return response

#========================================== Request handler ===============================================	
## GET query token value for specific key
@app.route('/tendersrv/getToken', methods=['GET'])
def getToken():
    ## 1) parse data from request.data
    key_str=TypesUtil.bytes_to_string(request.data)
    query_json = {}
    query_json['data']=key_str

    ## call abci_query
    query_ret=PRC_Client.abci_query(query_json)

    ## prepare response
    response = {}
    response['id']=key_str
    value_str = query_ret['result']['response']['value']
    if(value_str != None):
        response['value']= TypesUtil.base64_to_ascii(value_str)
    else:
        response['value']='None'

    return jsonify(response), 200

## POST set token value given specific key
@app.route('/tendersrv/setToken', methods=['POST'])
def setToken():
    '''
    submit token data to tendermint ledger
    '''
    req_data=TypesUtil.bytes_to_string(request.data)

    ret_json=json.loads(req_data)
    token_json = ret_json['value']
    if(token_json=='{}'):
        abort(401, {'error': 'No token data'})

    ## build value data from token_json.
    key_str = ret_json['key']
    token_str = TypesUtil.json_to_tx(token_json)
    tx_data = '"' + key_str + "=" + token_str + '"'

	## --------- build parameter string: tx=? --------
    tx_json = {}
    tx_json['tx']=tx_data

    ## call broadcast_tx_commit
    commit_ret = PRC_Client.broadcast_tx_commit(tx_json)

    # print(commit_ret)
    
    respose_json = {}
    respose_json['id']=key_str

    if('error' in commit_ret):
        respose_json['value']=commit_ret['error']
    else:
        respose_json['value'] = commit_ret['result']['hash']

    return jsonify(respose_json), 200

def define_and_get_arguments(args=sys.argv[1:]):
	parser = ArgumentParser(description="Run Fed-DDM Broker websocket server.")

	parser.add_argument('-p', '--port', default=80, type=int, 
						help="port to listen on.")
	parser.add_argument("--debug", action="store_true", 
						help="if set, debug model will be used.")
	parser.add_argument("--threaded", action="store_true", 
						help="if set, support threading request.")

	args = parser.parse_args()
	return args
    
if __name__ == '__main__':
    ## get arguments
    args = define_and_get_arguments()
        
    app.run(host='0.0.0.0', port=args.port, debug=args.debug, threaded=args.threaded)
