#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-03-27 08:04:24
LastEditors: wangruoyu
LastEditTime: 2023-03-27 08:04:32
Description: file content
FilePath: /chopchop_crispr_cdk/lambda/jobs/app.py
'''
import os
import boto3
import json
import uuid
import time
import re
import sys

dynamodb = boto3.resource('dynamodb',region_name=os.environ['AWS_DEFAULT_REGION'])
result_table = dynamodb.Table(os.environ['ddbResult'])

def get_item(jobid):
    response = result_table.get_item(
            Key={
                "jobid":jobid
                }
        )
    print(response)
    if 'Item' in response:
        return response["Item"]
    else:
        return False

def lambda_handler(event,context):
    """
    event = {
        "ids":[]
    }      
    """
    try:
        print(event)
        dictall = []
        for i in event["ids"]:
            res = get_item(i)
            if res:
                if 'output' in res:
                    del res['output']
                if "params" in res:
                    if res["type"] == "edit":
                        if "chopchop_jobid" in res["params"]:
                            chopchop_jobid = res["params"]["chopchop_jobid"]
                            del res["params"]
                        else:
                            chopchop_jobid=""
                        res["params"] = {}
                        res["params"]["chopchop_jobid"] = chopchop_jobid
                dictall.append(res)
        return {
            "statusCode":200,
            "data":dictall
            }
        
    except Exception as e:
        print(str(e))
        return {
            "statusCode":500,
            "msg":str(e)
        }