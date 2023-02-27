import os
import sys
import boto3
import uuid

import pandas as pd
import xlsxwriter
from Bio import SeqIO

from edit_sequence_design import main as edit_sd

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

        "chopchop_input": "s3://chopchop-prod/info_input.csv",
        "sgRNA_result_path": "s3://chopchop-prod/all_result.csv",
        "edit_sequence_design_workdir":"./output/edit_sequence_design/",

        "one_plasmid_file_path": "s3://chopchop-prod/pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        "no_ccdb_plasmid":"s3://chopchop-prod//no-ccdb-pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        "no_sgRNA_plasmid":"s3://chopchop-prod/no-sgRNA-pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        
        "plasmid_label":{
            "ccdb_label":"ccdB",
            "promoter_terminator_label":"gRNA",
            "n_20_label":"N20"
        },
        
        "sgRNA_primer_json":{
            "primer3":"AACTATTTATCCAGTTGGTACAAAC",
            "primer5":"GAAGATAACGAACAAAAACAATTGT"
        },
        "ccdb_primer_json":{
            "primer3":"AACTGATTCAGTCTGATTTCGCGGT",
            "primer5":"CCCTCTAATCGAAACTAATGGGGA"
        },
    
        "sgRNA_region_json":{
            "region1":"371,570",
            "region2":"3572,3770"
        },
        
        "ccdb_region_json":{
            "region1":"8364,8563",
            "region2":"376,575"
        },
        
        "S_GLOBAL_ARGS":{
            "PRIMER_OPT_SIZE": 20,   
            "PRIMER_MIN_SIZE": 18,
            "PRIMER_MAX_SIZE": 25,
            "PRIMER_OPT_TM": 65.0,
            "PRIMER_MIN_TM": 55.0,
            "PRIMER_MAX_TM": 75.0,
            "PRIMER_MIN_GC": 20.0,
            "PRIMER_MAX_GC": 80.0
        },
        
        "Q_ARGS":{
            "PRIMER_OPT_SIZE": 20,
            "PRIMER_MIN_SIZE": 18,   
            "PRIMER_MAX_SIZE": 25,
            "PRIMER_OPT_TM": 65.0,
            "PRIMER_MIN_TM": 55.0,
            "PRIMER_MAX_TM": 75.0,    
            "PRIMER_MIN_GC": 20.0,
            "PRIMER_MAX_GC": 80.0
        },
    
        "enzyme":{
            "name":"BsaI",
            "protective_base":"CCA",
            "recognition_seq":"GGTCTC",
            "cut_seq_len":4,
            "gap_len":1    
        }

    }
    """
    print(event)
    try:
        # 读写路径
        jobid = event['jobid']
        workdir = f'/tmp/{jobid}'
        print(f'working dir: {workdir}')
        os.mkdir(workdir)
        os.chdir(workdir)
        event["edit_sequence_design_workdir"] = workdir
        
        #下载数据 并重置参数
        keys = [
            "chopchop_input","sgRNA_result_path","one_plasmid_file_path",
            "no_ccdb_plasmid","no_sgRNA_plasmid",
        ]
        for key in keys:
            event[key] = download_s3_file(event[key],workdir)
        
        output_file = edit_sd.main(event)
        
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
    event = {
        
    }