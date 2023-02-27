#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:38:18
LastEditors: wangruoyu
LastEditTime: 2023-02-16 07:22:11
Description: file content
FilePath: /chopchop_crispr_cdk/lambda/data_preprocessing/app.py
'''
import os
import sys
import uuid

import boto3
import pandas as pd
import xlsxwriter
from Bio import SeqIO

from data_preprocessing import parse_input_to_df as data_pp

result_bucket = os.environ["s3Result"]
s3 = boto3.resource('s3')

def download_s3_file(s3_file,workdir):
    """
    从s3下载文件
    :param s3_file: _description_
    :type s3_file: _type_
    :param workdir: _description_
    :type workdir: _type_
    """
    bucket = s3_file.split('/')[2]
    filename = s3_file.split('/')[-1]
    obj_key = '/'.join(s3_file.split('/')[3:])
    
    local_file = os.path.join(
        workdir,
        filename
    )
    s3.Object(bucket, obj_key).download_file(local_file)
    return local_file

def lambda_handler(event,context):
    """
    :param event: _description_
    :type event: _type_
    :param context: _description_
    :type context: _type_
    :return: _description_
    :rtype: _type_
   
    event = {
        "input_file_path":"s3://chopchop-prod/test/data_preprocessing/editor_info.csv",
        "ref_genome":"s3://chopchop-prod/test/data_preprocessing/GCA_000011325.1_ASM1132v1_genomic.fna",
        "uha_dha_config": {
            "max_right_arm_seq_length": 1050,
            "max_left_arm_seq_length": 1050,
            "min_left_arm_seq_length": 1000,
            "min_right_arm_seq_length": 1000
        }
    }
    """
    print(event)
    try:
        # 读写路径
        jobid = str(uuid.uuid4())
        workdir = f'/tmp/{jobid}'
        print(f'working dir: {workdir}')
        os.mkdir(workdir)
        os.chdir(workdir)
        event["data_preprocessing_workdir"] = workdir
        
        #下载数据 并重置参数
        event["input_file_path"] = download_s3_file(event["input_file_path"],workdir)
        event["ref_genome"] = download_s3_file(event["ref_genome"],workdir)
        
        output_file = data_pp.main(event)
        
        # 上传结果文件
        output_file_key = f"result/{jobid}/{output_file.split('/')[-1]}"
        s3.meta.client.upload_file(output_file, result_bucket, output_file_key)
        print(f'upload result file: {output_file_key} ')
        return {
            "statusCode":200,
            "data":output_file
        }
    except Exception as e:
        print(e)
        return {
            "statusCode":500,
            "msg":str(e)
        }
    finally:
        os.system(f'rm -rf {workdir}')
        print(f"delete working dir: {workdir}")
    
    
if __name__ == "__main__":
    
    # s3文件测试
    event = {
        "input_file_path":"s3://chopchop-prod/test/data_preprocessing/editor_info.csv",
        "ref_genome":"s3://chopchop-prod/test/data_preprocessing/GCA_000011325.1_ASM1132v1_genomic.fna",
        "data_preprocessing_workdir":"/home/wang_ry/tmp/data_preprocessing/output/",
        "uha_dha_config": {
            "max_right_arm_seq_length": 1050,
            "max_left_arm_seq_length": 1050,
            "min_left_arm_seq_length": 1000,
            "min_right_arm_seq_length": 1000
        }
    }
    lambda_handler(event,{})