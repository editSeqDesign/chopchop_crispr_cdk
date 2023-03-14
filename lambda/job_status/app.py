#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-03-14 01:38:51
LastEditors: wangruoyu
LastEditTime: 2023-03-14 01:56:32
Description: file content
FilePath: /chopchop_crispr_cdk/lambda/job_status/app.py
'''
import os
import sys
import boto3
import json

dynamodb = boto3.resource('dynamodb',region_name=os.environ['AWS_DEFAULT_REGION'])
result_table = dynamodb.Table(os.environ['ddbResult'])

def update_item(jobid,result:list,output:dict,status:str,error:str):
    """_summary_

    :param result: _description_
    :type result: list
    :param output: _description_
    :type output: dict
    :param status: _description_
    :type status: str
    :param error: _description_
    :type error: str
    :return: _description_
    :rtype: _type_
    """
    res = result_table.update_item(
        Key={
            "jobid": jobid,
        },
        ReturnValues="ALL_NEW",
        UpdateExpression ='SET #ts1 = :val1,#ts2 = :val2, #ts3 = :val3,#ts4 = :val4',
        ExpressionAttributeValues={
            ':val1':result,
            ':val2':output,
            ':val3':status,
            ':val4':error,
        },
        ExpressionAttributeNames={
            "#ts1": "result",
            "#ts2": "output",
            "#ts3": "status",
            "#ts4": "error",
        }
    )
    print(res)
    return res['Attributes']

def lambda_handler(event,context):
    """_summary_

    :param event: _description_
    :type event: _type_
    :param context: _description_
    :type context: _type_
    """
    print(event)
    result = []
    status = "Finished"
    output_dict = {}
    msg = ""
    if "error" in event:
        msg = event["error"]["Cause"]
        status = "Failed"
    else:
        for module in event["result"]:
            statusCode = event["result"][module]['Payload']["statusCode"]
            if statusCode == 200:
                output_file = event["result"][module]['Payload']["output_file"]
                output_dict[module] = output_file
                print(output_file)
                if module == "chopchop" or module == "edit":
                    for i in output_file:
                        obj_key = "/".join(i.split('/')[3:])
                        print(i,obj_key)
                        result.append(obj_key)
            elif statusCode == 500:
                msg += event["result"][module]['Payload']["msg"] +"; "
                status = "Failed"
    
    # update ddb item
    print(update_item(event["jobid"],result,output_dict,status,msg))
if __name__ == "__main__":
    pass