'''
========================
client_demo module
========================
Created on June.2, 2023
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide encapsulation of client API that access to Web service.
'''
import sys
import os
import datetime
import time
import argparse
import random
import threading

from service_api import SrvAPI
from utilities import FileUtil, DatetimeUtil, TypesUtil

class ReqThread (threading.Thread):
	'''
	Threading class to handle requests by multiple threads pool
	'''
	def __init__(self, threadID, ReqType, argv):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.ReqType = ReqType
		self.argv = argv

	## The run() method is the entry point for a thread.
	def run(self):
		# Add task operation here
		# print ("Starting ReqThread:{}".format(self.threadID))

		# Launch request given ReqType-0: query; 1: tx_commit;
		if(self.ReqType==1):
			tx_ret=WSClient.Set_DataByID(self.argv[0], self.argv[1])
			# print(tx_ret)
		else:
			query_ret=WSClient.Get_DataByID(self.argv[0], self.argv[1])
			# print(query_ret)

class WSClient(object):
    
    '''
    Get value by id
    '''
    @staticmethod
    def Get_DataByID(target_address, key_value):          
        json_response=SrvAPI.GET('http://'+target_address+'/tendersrv/getToken', key_value)
        return json_response
    
    '''
    Set value by id
    '''
    @staticmethod
    def Set_DataByID(target_address, key_value):          
        json_response=SrvAPI.POST('http://'+target_address+'/tendersrv/setToken', key_value)
        return json_response
    
    '''
    Random get a service node address
    '''
    @staticmethod
    def get_service_address():          
        services_host = FileUtil.JSON_load('api_server.json')
        server_id = random.randint(0,len(services_host['all_nodes'])-1)

        target_address = services_host['all_nodes'][server_id]

        return target_address

def demo_query(args):
    target_address = args.target_address
    key_id = args.key_id

    start_time=time.time()
    print(WSClient.Get_DataByID(target_address, key_id))
    exec_time=time.time()-start_time
    print(format(exec_time*1000, '.3f'))
    FileUtil.save_testlog('test_results', 'get_Token.log', format(exec_time*1000, '.3f'))

def demo_commit(args): 
    target_address = args.target_address
    key_id = args.key_id

    ## build dummy AC token
    token_json = {}
    token_json['user'] = "samuelxu999"
    token_json['type'] = "CapAC_token"
    token_json['ac'] = {}
    token_json['ac']['resource'] = "/test/api/v1.0/dt"
    token_json['ac']['action'] = "GET"
    token_json['ac']['conditions'] = "MWF, start:8:12:32 and end:14:32:32"
    token_json['ac']['timestamp'] = DatetimeUtil.datetime_timestamp(datetime.datetime.now())
    token_json['ac']['nonce'] = TypesUtil.string_to_hex(os.urandom(6))

    tx_json = {}
    tx_json['key']= key_id
    tx_json['value']=token_json

    start_time=time.time()
    print(WSClient.Set_DataByID(target_address, tx_json))
    exec_time=time.time()-start_time
    print(format(exec_time*1000, '.3f'))
    FileUtil.save_testlog('test_results', 'set_Token.log', format(exec_time*1000, '.3f')) 

def thread_query(args):
    key_id = args.key_id
    thread_count = args.tx_thread

    # Create thread pool
    threads_pool = []
    i=0

    for i in range(1,thread_count+1):
        target_address = WSClient.get_service_address()
        search_key = key_id + str(i)

        # Create new threads
        p_thread = ReqThread(i, 0, [ target_address, search_key])

        # append to threads pool
        threads_pool.append(p_thread)

        # The start() method starts a thread by calling the run method.
        p_thread.start()
        

    # The join() waits for all threads to terminate.
    for p_thread in threads_pool:
        p_thread.join()

def thread_commit(args):
    key_id = args.key_id
    thread_count = args.tx_thread

    # Create thread pool
    threads_pool = []
    i=0

    for i in range(1,thread_count+1):
        target_address = WSClient.get_service_address()

        ## build dummy AC token
        token_json = {}
        token_json['user'] = "samuelxu999"
        token_json['type'] = "CapAC_token"
        token_json['ac'] = {}
        token_json['ac']['resource'] = "/test/api/v1.0/dt"
        token_json['ac']['action'] = "GET"
        token_json['ac']['conditions'] = "MWF, start:8:12:32 and end:14:32:32"
        token_json['ac']['timestamp'] = DatetimeUtil.datetime_timestamp(datetime.datetime.now())
        token_json['ac']['nonce'] = TypesUtil.string_to_hex(os.urandom(6))

        tx_json = {}
        tx_json['key']= key_id + str(i)
        tx_json['value']=token_json

        # Create new threads
        p_thread = ReqThread(i, 1, [ target_address, tx_json])

        # append to threads pool
        threads_pool.append(p_thread)

        # The start() method starts a thread by calling the run method.
        p_thread.start()
        

    # The join() waits for all threads to terminate.
    for p_thread in threads_pool:
        p_thread.join()

def define_and_get_arguments(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Run websocket client.")

    parser.add_argument("--test_func", type=int, default=0, help="test function: \
                                                            0: infromation query ")
    parser.add_argument("--op_status", type=int, default=0, help="operational function mode")
    parser.add_argument("--tx_size", type=int, default=128, help="Size of value in transaction.")
    parser.add_argument("--tx_thread", type=int, default=10, help="Transaction-threads count.")
    parser.add_argument("--test_round", type=int, default=1, help="test evaluation round")
    parser.add_argument("--wait_interval", type=int, default=1, help="break time between step.")
    parser.add_argument("--target_address", type=str, default="0.0.0.0:8088", 
                        help="Test target address - ip:port.")
    parser.add_argument("--key_id", type=str, default="", 
                        help="Input date for test.")
    args = parser.parse_args(args=args)
    return args

if __name__ == "__main__":
    ## get arguments
    args = define_and_get_arguments()
        
    if(args.test_func==1):
        for x in range(args.test_round):
            print("Test run:", x+1)
            if(args.op_status==1):
                start_time=time.time()
                thread_commit(args)
                exec_time=time.time()-start_time
                print(format(exec_time*1000, '.3f'))
                FileUtil.save_testlog('test_results', 'thread_commit.log', format(exec_time*1000, '.3f')) 
            else:
                start_time=time.time()
                thread_query(args)
                exec_time=time.time()-start_time
                print(format(exec_time*1000, '.3f'))
                FileUtil.save_testlog('test_results', 'thread_query.log', format(exec_time*1000, '.3f')) 
            
            time.sleep(args.wait_interval)
    else:
        if(args.op_status==1):
            demo_commit(args)
        else:
            demo_query(args)
 