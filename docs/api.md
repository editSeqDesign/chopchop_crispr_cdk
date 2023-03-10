
# API

## 1. primary 分析 chopchop

执行chopchop计算

**请求URL:**

+   `/api/chopchop`

**请求方式**

+   POST

**参数**

| 参数名   | 必选 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| data |  是    |     dict |   data_preprocessing 参数   |
| chopchop |  是    |     dict |  chopchop 参数 |


**参数示例**


```python
# 执行chopchop计算
# data  产生的info_input.csv是 chopchop的input_file_path
{
    
    "data":{
        "input_file_path":"s3://chopchop-prod/test/data_preprocessing/editor_info.csv",
        "ref_genome":"s3://chopchop-prod/test/data_preprocessing/GCA_000011325.1_ASM1132v1_genomic.fna"
    },
    "chopchop":{
        "PAM": "NGG",  
        "guideSize": 20,
        "maxMismatches": 3,
        "scoringMethod": "DOENCH_2014"
    }
}



```




# 2. 编辑序列设计 edit

**请求URL:**

+   `/api/edit`

**请求方式**

+   POST

**参数**

| 参数名   | 必选 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| chopchop_jobid |  是    |     string |     |
| one_plasmid_file_path |  是    |     string |   |
| no_ccdb_plasmid |  是    |     string |   |
| no_sgRNA_plasmid |  是    |     string |   |
| uha_dha_config |  是    |     dict |   |
| plasmid_label |  是    |     dict |   |
| sgRNA_primer_json |  是    |     dict |   |
| ccdb_primer_json |  是    |     dict |   |
| sgRNA_region_json |  是    |     dict |   |
| ccdb_region_json |  是    |     dict |   |
| enzyme |  是    |     dict |   |
| UHA_ARGS |  是    |     dict |   |
| SEQ_ALTERED_ARGS |  是    |     dict |   |
| DHA_ARGS |  是    |     dict |   |
| UP_SGRNA_ARGS |  是    |     dict |   |
| DOWN_SGRNA_ARGS |  是    |     dict |   |
| PLASMID_Q_ARGS |  是    |     dict |   |
| GENOME_Q_ARGS |  是    |     dict |   |


**参数示例**


```python

# 执行edit 编辑序列设计
# 1.如果提供jobid，chopchop_input，sgRNA_result_path，ref_genome的值可以缺省
# 2.用户自定义上传，需要提供chopchop_input，sgRNA_result_path，ref_genome，并执行data模块
{
        "chopchop_jobid":"6787a2cf-0a42-4bff-ad05-89d24e7e81fa",
        "one_plasmid_file_path": "s3://chopchop-prod/pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        "no_ccdb_plasmid":"s3://chopchop-prod/no-ccdb-pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        "no_sgRNA_plasmid":"s3://chopchop-prod/no-sgRNA-pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
        "uha_dha_config": {
            "max_right_arm_seq_length": 1050,
            "max_left_arm_seq_length": 1050,
            "min_left_arm_seq_length": 1000,   
            "min_right_arm_seq_length": 1000
        },

        
        "plasmid_label":{
            "ccdb_label":"ccdB",
            "promoter_terminator_label":"gRNA",
            "n_20_label":"N20"
        },
        
        "sgRNA_primer_json":{
            "primer3":"AACTATTTATCCAGTTGGTACAAAC"
        },
        "ccdb_primer_json":{
            "primer3":"AACTGATTCAGTCTGATTTCGCGGT"
        },
    
        "sgRNA_region_json":{
            "region1":"tgtgtggaattgtgagcggataacaatttcacacaggaaacagaatt"
        },
        
        "ccdb_region_json":{
            "region1":"ATTGTGAGCGGATAACAATTTCACACAGGAAACAGAATTAATTAAGCTTAAAGGAGTTGAGAATGGATAAGAAATACTCAATAGGCTTAGATATCGGCACAAATAGCGTCGGATGGGCGGTGATC"
        },
        
        "enzyme":{
            "enzyme_name":"BsaI",
            "gap_sequence":"A",
            "protection_sequence":"CCA"
        },
        
        "UHA_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,
            "PRIMER_MAX_TM": 75,
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },
        "SEQ_ALTERED_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,
            "PRIMER_MAX_TM": 75,  
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },
        "DHA_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,
            "PRIMER_MAX_TM": 75,
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },
        "UP_SGRNA_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,
            "PRIMER_MAX_TM": 75,
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },
        "DOWN_SGRNA_ARGS": {
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,
            "PRIMER_MAX_TM": 75,
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },

        "PLASMID_Q_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,  
            "PRIMER_MAX_TM": 75,    
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        },
        "GENOME_Q_ARGS":{
            "PRIMER_OPT_TM": 65,
            "PRIMER_MIN_TM": 55,  
            "PRIMER_MAX_TM": 75,    
            "PRIMER_MIN_GC": 20,
            "PRIMER_MAX_GC": 80
        }
    }
```

# 3. 获取任务详情  jobs

**请求URL:**

+   `/api/jobs`

**请求方式**

+   POST

**参数**

| 参数名   | 必选 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| ids |  是    |     list(string )|     |


**参数示例**

```python
{
    "ids":[]
}


```