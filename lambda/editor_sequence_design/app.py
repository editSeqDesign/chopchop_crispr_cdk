import os
import sys
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
MODULE_DIR = os.path.join(ROOT_DIR,"editor_sequence_design")
sys.path.append(MODULE_DIR)
import boto3
import uuid

import pandas as pd
import xlsxwriter
from Bio import SeqIO

from editor_sequence_design import main as edit_sd

result_bucket = os.environ["s3Result"]
reference_bucket = os.environ["s3Reference"]

s3 = boto3.resource('s3')

dynamodb = boto3.resource('dynamodb',region_name=os.environ['AWS_DEFAULT_REGION'])
result_table = dynamodb.Table(os.environ['ddbResult'])

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
        # 根据chopchop_jobid获取chopchop_input，sgRNA_result_path，ref_genome
        # check chopchop_jobid 
        chopchop_jobid = event["chopchop_jobid"]
        response = result_table.get_item(Key={'jobid':chopchop_jobid })
        if not 'Item' in response:
            raise ValueError(f"The chopchop jobid {chopchop_jobid} is not exists.")
        else:
            if response['Item']['status'] != "Finished":
                raise ValueError(f"The chopchop jobid {chopchop_jobid} is {response['Item']['status']}, can not be used to run edit sequence design")

        event["chopchop_input"] = response['Item']['output']["data"]
        event["sgRNA_result_path"] = response['Item']['output']["chopchop"][1]
        event["ref_genome"] = response['Item']['params']["data"]["ref_genome"]
        #下载数据 并重置参数
        keys = ["chopchop_input","sgRNA_result_path","ref_genome",      "one_plasmid_file_path","no_ccdb_plasmid","no_sgRNA_plasmid",
        ]
        for key in keys:
            if event[key]:
                print(key,event[key])
                if key == "ref_genome":
                    if event["ref_genome"].startswith('reference/'):
                        event[key] = f"s3://{reference_bucket}/{event['ref_genome']}" 
                event[key] = download_s3_file(event[key],workdir)
        
        response = edit_sd.main(event)
        if isinstance(response,str):
            # 上传结果文件
            output_file = response
            output_file_key = f"result/{jobid}/{output_file.split('/')[-1]}"
            s3.meta.client.upload_file(output_file, result_bucket, output_file_key,ExtraArgs={'ACL': "public-read"})
            print(f'upload result file: {output_file_key} ')
            return {
                "statusCode":200,
                "output_file":[f"s3://{result_bucket}/{output_file_key}"]
            }
        elif isinstance(response,tuple):
            output_file_list =[]
            for output_file in response:
                output_file_key = f"result/{jobid}/{output_file.split('/')[-1]}"
                s3.meta.client.upload_file(output_file, result_bucket, output_file_key,ExtraArgs={'ACL': "public-read"})
                print(f'upload result file: {output_file_key} ')
                output_file_list.append(f"s3://{result_bucket}/{output_file_key}")
            return {
                "statusCode":200,
                "output_file":output_file_list
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
    "chopchop_jobid": "e952af24-0e18-4cdb-97b4-f6cee77e8ded",
    "one_plasmid_file_path": "s3://chopchop-prod/public/1678777751777/single.gb",
    "no_ccdb_plasmid": "",
    "no_sgRNA_plasmid": "",
    "sgRNA_result": {
      "Cgl1386_327_18to15_sub": 1,
      "Cgl1436_1113_CAA_del": 1,
      "153019_ecoil_ybeL_ins": 1,
      "Cgl0141_cds_del": 1,
      "Cgl1790_1647_TCC_sub": 1,
      "Cgl2342_213_GCA_ins": 1,
      "Cgl0591_-1_Ppgk_promoter_ins": 1,
      "Cgl0006_1176_G_A_sub": 1,
      "Cgl0851_ecoli_pgi_sub": 1
    },
    "uha_dha_config": {
      "max_right_arm_seq_length": 1050,
      "max_left_arm_seq_length": 1050,
      "min_left_arm_seq_length": 1000,
      "min_right_arm_seq_length": 1000
    },
    "plasmid_label": {
      "ccdb_label": "ccdB",
      "promoter_terminator_label": "gRNA",
      "n_20_label": "N20"
    },
    "primer_json": {
      
    },
    "region_json": {
      
    },
    "sgRNA_primer_json": {
      
    },
    "ccdb_primer_json": {
      
    },
    "sgRNA_region_json": {
      
    },
    "ccdb_region_json": {
      
    },
    "enzyme": {
      "enzyme_name": "BsaI",
      "gap_sequence": "A",
      "protection_sequence": "CCA"
    },
    "UHA_ARGS": {
      "PRIMER_OPT_TM": 60,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "SEQ_ALTERED_ARGS": {
      "PRIMER_OPT_TM": 60,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "DHA_ARGS": {
      "PRIMER_OPT_TM": 55,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "UP_SGRNA_ARGS": {
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "DOWN_SGRNA_ARGS": {
      "PRIMER_OPT_TM": 60,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "PLASMID_Q_ARGS": {
      "PRIMER_OPT_TM": 60,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "GENOME_Q_ARGS": {
      "PRIMER_OPT_TM": 60,
      "PRIMER_MIN_TM": 55,
      "PRIMER_MAX_TM": 65,
      "PRIMER_MIN_GC": 30,
      "PRIMER_MAX_GC": 70
    },
    "jobid": "8d14d0ed-dca3-4bbc-9906-9278ccbba95f"
  }
    
    print(lambda_handler(event,{}))