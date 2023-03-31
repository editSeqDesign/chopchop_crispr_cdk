
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
| scene |  是    |     string | only_sgRNA,both_sgRNA_primer |


**参数示例**


```python
# 执行chopchop计算
# data  产生的info_input.csv是 chopchop的input_file_path
# scene : only_sgRNA,both_sgRNA_primer
{
    "data":{
        "input_file_path":"s3://chopchop-prod/public/1678763674305/editor_info.csv",
        "ref_genome":"s3://chopchop-prod/public/1678763668969/GCA_000011325.1_ASM1132v1_genomic.fna"
    },
    "chopchop":{
        "PAM":"NGG",
        "guideSize":20,
        "maxMismatches":3,
        "scoringMethod":"DOENCH_2014"
    },
    "scene":"both_sgRNA_primer"
}

# only sgRNA
{
    "data":{
        "input_file_path":"s3://chopchop-prod/test/only_sgRNA_design.csv",
        "ref_genome":"s3://chopchop-prod/public/1678763668969/GCA_000011325.1_ASM1132v1_genomic.fna"
    },
    "chopchop":{
        "PAM":"NGG",
        "guideSize":20,
        "maxMismatches":3,
        "scoringMethod":"DOENCH_2014"
    },
    "scene":"only_sgRNA"
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
| chopchop_jobid |  否    |     string |  scene=both_sgRNA_primer，必选  |
| input_file_path |  否    |     string |   scene=only_primer，必选  |
| ref_genome |  否    |     string | scene=only_primer ，必选   |
| scene |  是    |     string |   only_primer,both_sgRNA_primer  |
| one_plasmid_file_path |  是    |     string |   |
| no_ccdb_plasmid |  是    |     string |   |
| no_sgRNA_plasmid |  是    |     string |   |
| uha_dha_config |  是    |     dict |   |
| plasmid_label |  是    |     dict |   |
| sgRNA_primer_json |  是    |     dict |   |
| ccdb_primer_json |  是    |     dict |   |
| region_label |    是     |    string |    |
| sgRNA_region_label |  是    |    string |   |
| ccdb_region_label |  是    |     string |   |
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

# scene: only_primer, both_sgRNA_primer

# only_primer: input_file_path和ref_genome 要上传
{
    "input_file_path":"s3://chopchop-prod/test/only_primer.csv",
    "ref_genome":"s3://chopchop-prod/public/1678763668969/GCA_000011325.1_ASM1132v1_genomic.fna"
    "one_plasmid_file_path":"s3://chopchop-prod/pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
    "no_ccdb_plasmid":"",
    "no_sgRNA_plasmid":"",
    "sgRNA_result":{
        
    },
    "uha_dha_config":{
        "max_right_arm_seq_length":1050,
        "max_left_arm_seq_length":1050,
        "min_left_arm_seq_length":1000,
        "min_right_arm_seq_length":1000
    },
    "plasmid_label":{
        "ccdb_label":"ccdB",
        "promoter_terminator_label":"gRNA",
        "n_20_label":"N20"
    },
    "primer_json":{

    },
    
    "region_label":"",

    "sgRNA_primer_json":{

    },
    "ccdb_primer_json":{

    },

    "sgRNA_region_label":"",
    "ccdb_region_label":"",

    "enzyme":{
        "enzyme_name":"BsaI",
        "gap_sequence":"A",
        "protection_sequence":"CCA"
    },
    "UHA_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "SEQ_ALTERED_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "DHA_ARGS":{
        "PRIMER_OPT_TM":55,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "UP_SGRNA_ARGS":{
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "DOWN_SGRNA_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "PLASMID_Q_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "GENOME_Q_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "scene":"only_primer"
}
# both_sgRNA_primer：  chopchop_jobid非空
{
    "chopchop_jobid":"3e2af881-ef8f-4202-aa3c-e45d209d1914",
    "one_plasmid_file_path":"s3://chopchop-prod/pXMJ19-Cas9A-gRNA-crtYEb-Ts - ori.gb",
    "no_ccdb_plasmid":"",
    "no_sgRNA_plasmid":"",
    "sgRNA_result":{
        "Cgl1386_327_18to15_sub":1,
        "Cgl1436_1113_CAA_del":1,
        "153019_ecoil_ybeL_ins":1,
        "Cgl0141_cds_del":1,
        "Cgl1790_1647_TCC_sub":1,
        "Cgl2342_213_GCA_ins":1,
        "Cgl0591_-1_Ppgk_promoter_ins":1,
        "Cgl0006_1176_G_A_sub":1,
        "Cgl0851_ecoli_pgi_sub":1
    },
    "uha_dha_config":{
        "max_right_arm_seq_length":1050,
        "max_left_arm_seq_length":1050,
        "min_left_arm_seq_length":1000,
        "min_right_arm_seq_length":1000
    },
    "plasmid_label":{
        "ccdb_label":"ccdB",
        "promoter_terminator_label":"gRNA",
        "n_20_label":"N20"
    },
    "primer_json":{

    },
    "region_label":"",
    "sgRNA_primer_json":{

    },
    "ccdb_primer_json":{

    },
    "sgRNA_region_json":"",
    "ccdb_region_json":"",
    "enzyme":{
        "enzyme_name":"BsaI",
        "gap_sequence":"A",
        "protection_sequence":"CCA"
    },
    "UHA_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "SEQ_ALTERED_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "DHA_ARGS":{
        "PRIMER_OPT_TM":55,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "UP_SGRNA_ARGS":{
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "DOWN_SGRNA_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "PLASMID_Q_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "GENOME_Q_ARGS":{
        "PRIMER_OPT_TM":60,
        "PRIMER_MIN_TM":55,
        "PRIMER_MAX_TM":65,
        "PRIMER_MIN_GC":30,
        "PRIMER_MAX_GC":70
    },
    "scene":"both_sgRNA_primer"
}

# only primer

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
# 查询edit
{
    "ids":["cea2a2cb-a3f3-4c38-b147-df9461abf981"]
}


```


**返回示例**
```python

# 查询edit 结果
{
    "statusCode":200,
    "data":[
        {
            "status":"Finished",
            "timestamp":"1678861294",
            "jobid":"cea2a2cb-a3f3-4c38-b147-df9461abf981",
            "result":{
                "one":{
                    "xlsx":"result/cea2a2cb-a3f3-4c38-b147-df9461abf981/one_plasmid_system_gb/one_plasmid_design_result.xlsx",
                    "tsv":"cea2a2cb-a3f3-4c38-b147-df9461abf981/one_plasmid_system_gb/gb_visualization.tsv"
                }
            },
            "error":"",
            "type":"edit",
            "params":{
                "chopchop_jobid":"a373c204-f316-4696-a322-dd1a149aaeb8"
            }
        }
    ]
}

```