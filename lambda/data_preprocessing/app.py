#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:38:18
LastEditors: wangruoyu
LastEditTime: 2023-03-14 05:19:38
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
reference_bucket = os.environ["s3Reference"]
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
    
    jobid = event["jobid"]
    workdir = f'/tmp/{jobid}'
    print(f'working dir: {workdir}')
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    os.chdir(workdir)
    event["data_preprocessing_workdir"] = workdir
    
    #下载数据 并重置参数
    event["input_file_path"] = download_s3_file(event["input_file_path"],workdir)

    if event["ref_genome"].startswith('reference/'):
        event["ref_genome"] = f"s3://{reference_bucket}/{event['ref_genome']}" 
    event["ref_genome"] = download_s3_file(event["ref_genome"],workdir)
    
    print('begin:',event)
    output_file = data_pp.main(event)
    
    # 上传结果文件
    if type(output_file) == str:
        output_file_key = f"result/{jobid}/data/{output_file.split('/')[-1]}"
        s3.meta.client.upload_file(output_file, result_bucket, output_file_key)
        print(f'upload result file: {output_file_key} ')
    elif type(output_file) == list:
        #1. editor_info
        editor_info = output_file[0]
        output_file_key1 = f"result/{jobid}/data/{editor_info.split('/')[-1]}"
        s3.meta.client.upload_file(editor_info, result_bucket, output_file_key1)
        print(f'upload result file: {output_file_key1} ')
        #2. ref_genome
        ref_genome = output_file[1]
        output_file_key2 = f"result/{jobid}/data/{ref_genome.split('/')[-1]}"
        s3.meta.client.upload_file(ref_genome, result_bucket, output_file_key2)
        print(f'upload result file: {output_file_key2} ')


    # delete workdir
    os.system(f'rm -rf {workdir}')
    print(f"delete working dir: {workdir}")
    
    if type(output_file) == str:
         return {
            "statusCode":200,
            "output_file": f"s3://{result_bucket}/{output_file_key}"
        }

    elif type(output_file) == list:
        return {
            "statusCode":200,
            "output_file": [f"s3://{result_bucket}/{output_file_key1}", f"s3://{result_bucket}/{output_file_key2}"]
        }
        
    
    
if __name__ == "__main__":
    
    # s3文件测试
    event1 = {
        "input_file_path":"s3://chopchop-prod/test/data_preprocessing/editor_info.csv",
        "ref_genome":"s3://chopchop-prod/test/data_preprocessing/GCA_000011325.1_ASM1132v1_genomic.fna",
        "data_preprocessing_workdir":"/home/wang_ry/tmp/data_preprocessing/output/"
    }
    event2 = {
        "input_file_path":"s3://chopchop-prod/test/data_preprocessing/4-20-input.csv",
        "ref_genome":"s3://chopchop-prod/test/data_preprocessing/GCF_000005845.2_ASM584v2_genomic.gbff",
        "data_preprocessing_workdir":"/home/wang_ry/tmp/data_preprocessing/output/",
        "jobid":"123",
        "scene":"both_sgRNA_primer"
    }
  

    lambda_handler(event2,{})