from flask import Flask, jsonify
from flask import abort,make_response,request
import datetime
import json


app = Flask(__name__)

now = datetime.datetime.now()
datestr=now.strftime("%Y-%m-%d")
timestr=now.strftime("%H:%M:%S")

#Defining dict
projects = [
    {
        'id': 1,
        'title':u'test',
        'description':u'Hello World',
        'date':u'04-28-2017',
        'time': u'Morning'
    },
    {
        'id': 2,
        'title':u'GET',
        'description':u'test GET APIs',
        'date':u'4-29-2017',
        'time': u'12:00 am'
    }
]


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
#GET req
@app.route('/test/api/v1.0/dt', methods=['GET'])
def get_projects():
    #Token missing, deny access
    if(request.data=='{}'):
        abort(401, {'message': 'Token missing, deny access'})        

    return jsonify({'result': 'Succeed', 'projects': projects}), 201
    
#GET req for specific ID
@app.route('/test/api/v1.0/dt/project', methods=['GET'])
def get_project():
    #Token missing, deny access
    if(request.data=='{}'):
        abort(401, {'message': 'Token missing, deny access'})
        
    #print request.data
    project_id = request.args.get('project_id', default = 1, type = int)
    #project_id = int(request.args['project_id'])
    
    project = [project for project in projects if project['id'] == project_id]
    if len(project) == 0:
        abort(404, {'message': 'No data found'})
    return jsonify({'result': 'Succeed', 'project': project[0]}), 201
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
