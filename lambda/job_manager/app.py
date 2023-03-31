#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-03-08 06:58:16
LastEditors: wangruoyu
LastEditTime: 2023-03-27 08:11:09
Description: file content
FilePath: /chopchop_crispr_cdk/lambda/job_manager/app.py
'''
import os
import sys
import uuid
import json
import time

import boto3  

dynamodb = boto3.resource('dynamodb',region_name=os.environ['AWS_DEFAULT_REGION'])
result_table = dynamodb.Table(os.environ['ddbResult'])

client = boto3.client('stepfunctions')
def api_response(statuscode,data):
    # lambda response to api gateway proxy lambda
    response = {
        "statusCode": statuscode,
        "headers":{
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(data)
    }
    return response


def ddb_item_dict(jobid,params,stype="chopchop"):
    dictall = {}
    dictall["jobid"] = jobid
    dictall['status'] = "Queued"
    dictall['timestamp'] = str(int(time.time()))
    dictall['type'] = stype
    dictall['params'] = params
    dictall['scene'] = params["scene"]
    dictall['result'] = {}
    dictall['error'] = ''
    return dictall
    
def lambda_handler(event,context):
    """_summary_

    :param event: _description_
    :type event: _type_
    :param context: _description_
    :type context: _type_
    :return: _description_
    :rtype: _type_
    """
    try:
        print(event)
        params = json.loads(event['body'])

        url_path = event["path"]
        jobid = str(uuid.uuid4())
        if url_path == "/api/chopchop":
            print("submit chopchop job......")
            dictall= ddb_item_dict(jobid,params)
            # create ddb item
            result_table.put_item(
                Item=dictall
            )
            # sfn submit
            params_copy = params.copy()
            params_copy["jobid"] = jobid
            client.start_execution(
                stateMachineArn=os.environ["sfnChopchop"],
                input=json.dumps(
                    params_copy
                    )
            )
            print('chopchop sfn submit....')
        elif url_path == "/api/edit":
            print('submit edit sequence job.....')
            dictall= ddb_item_dict(jobid,params,"edit")
            # create ddb item
            result_table.put_item(
                Item=dictall
            )
            # sfn submit
            params_copy = params.copy()
            params_copy["jobid"] = jobid
            client.start_execution(
                stateMachineArn=os.environ["sfnEdit"],
                input=json.dumps(
                    params_copy
                    )
            )
            print('edit sfn submit....')
        else:
            raise ValueError(f'{url_path} not support.')
        
        code = 200
        response = {
            "statusCode":code,
            "data":dictall
        }
        return api_response(code,response)
    except Exception as e:
        print(e)
        code = 500
        response = {
            "statusCode":code,
            "msg":str(e)
        }
        return api_response(code,response)
    