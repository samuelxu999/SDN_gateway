#!/usr/bin/env python

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
import requests
import json
import argparse

from service_api import SrvAPI, ReqThread, QueryThread

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
        
    target_address = args.target_address
    key_id = args.key_id
    
    if(args.test_func==1):
        ## build dummy AC token
        token_json = {}
        token_json['user'] = "samuelxu999"
        token_json['type'] = "CapAC_token"
        token_json['ac'] = {}
        token_json['ac']['resource'] = "/test/api/v1.0/dt"
        token_json['ac']['action'] = "GET"
        token_json['ac']['conditions'] = "MWF, start:8:12:32 and end:14:32:32"
     
        tx_json = {}
        tx_json['key']= key_id
        tx_json['value']=token_json

        print(WSClient.Set_DataByID(target_address, tx_json))
    else:
        print(WSClient.Get_DataByID(target_address, key_id))
