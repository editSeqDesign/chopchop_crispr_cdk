#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-03-08 07:06:43
LastEditors: wangruoyu
LastEditTime: 2023-03-27 06:04:47
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/stepfunctions_construct.py
'''
import os
import json

from aws_cdk import (
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_iam as iam,
    )
from constructs import Construct

class SfnConstruct(Construct):

    def __init__(self,scope:Construct,id:str,TargetLambda = "default",TargetBatch = "default",TargetS3="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self.step_functions = {}
        
        # error task
        error_task = sfn_tasks.LambdaInvoke(
                self,
                "job error",
                lambda_function = TargetLambda.get_lambda_functions("job_status"),
                payload= sfn.TaskInput.from_object({
                    "error": sfn.JsonPath.string_at("$.error"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                    
                }),
                result_path="$.Result.job_status"
            )
        
        #########################
        # chopchop stepfunctions
        
        # 1. data_preprocessing
        data_preprocessing_task = sfn_tasks.LambdaInvoke(
                self,
                "data_preprocessing",
                lambda_function = TargetLambda.get_lambda_functions("data_preprocessing"),
                payload= sfn.TaskInput.from_object({
                    "input_file_path": sfn.JsonPath.string_at("$.data.input_file_path"),
                    "ref_genome": sfn.JsonPath.string_at("$.data.ref_genome"),
                    "scene": sfn.JsonPath.string_at("$.scene"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                }),
                result_path="$.Result.data"
            )
        data_preprocessing_task.add_catch(
            error_task,
            result_path = "$.error"
        )
        # 2. chopchop 
        chopchop_task = sfn_tasks.LambdaInvoke(
                self,
                "run chopchop",
                lambda_function = TargetLambda.get_lambda_functions("chopchop"),
                payload= sfn.TaskInput.from_object({
                    "input_file_path": sfn.JsonPath.string_at("$.Result.data.Payload.output_file"),
                    "ref_genome": sfn.JsonPath.string_at("$.data.ref_genome"),
                    "chopchop_config": sfn.JsonPath.string_at("$.chopchop"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                }),
                result_path="$.Result.chopchop"
            )
        # job finished
        job_finish = sfn_tasks.LambdaInvoke(
                self,
                "job finished?",
                lambda_function = TargetLambda.get_lambda_functions("job_status"),
                payload= sfn.TaskInput.from_object({
                    "result": sfn.JsonPath.string_at("$.Result"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                    
                }),
                result_path="$.Result.job_status"
            )
        # catch error
        chopchop_task.add_catch(
            error_task,
            result_path = "$.error"
        )
        # chain
        chopchop_chain = sfn.Chain.start(data_preprocessing_task) \
                .next(chopchop_task) \
                .next(job_finish)
        # statemachine
        chopchop_statemachine = sfn.StateMachine(
            self,
            "chopchop",
            definition=chopchop_chain
        )

        self.step_functions["chopchop"] = chopchop_statemachine

        ############################################################
        # edit sfn
        
        edit_error_task = sfn_tasks.LambdaInvoke(
                self,
                "edit job error",
                lambda_function = TargetLambda.get_lambda_functions("job_status"),
                payload= sfn.TaskInput.from_object({
                    "error": sfn.JsonPath.string_at("$.error"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                    
                }),
                result_path="$.Result.job_status"
            )
        edit_dp_task = sfn_tasks.LambdaInvoke(
                self,
                "edit data_preprocessing",
                lambda_function = TargetLambda.get_lambda_functions("data_preprocessing"),
                payload= sfn.TaskInput.from_object({
                    "input_file_path": sfn.JsonPath.string_at("$.input_file_path"),
                    "ref_genome": sfn.JsonPath.string_at("$.ref_genome"),
                    "scene": sfn.JsonPath.string_at("$.scene"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                }),
                result_path="$.Result.data"
            )
        edit_dp_task.add_catch(
            edit_error_task,
            result_path = "$.error"
        )
        
        
        edit_only_task = sfn_tasks.LambdaInvoke(
                self,
                "run edit only primer",
                lambda_function = TargetLambda.get_lambda_functions("editor_sequence_design"),
                payload= sfn.TaskInput.from_object({
                    "scene": sfn.JsonPath.string_at("$.scene"),
                    "chopchop_input": sfn.JsonPath.string_at("$.Result.data.Payload.output_file"),
                    "ref_genome": sfn.JsonPath.string_at("$.ref_genome"),
                    "one_plasmid_file_path": sfn.JsonPath.string_at("$.one_plasmid_file_path"),
                    "no_ccdb_plasmid": sfn.JsonPath.string_at("$.no_ccdb_plasmid"),
                    "no_sgRNA_plasmid": sfn.JsonPath.string_at("$.no_sgRNA_plasmid"),
                    "uha_dha_config": sfn.JsonPath.string_at("$.uha_dha_config"),
                    "plasmid_label": sfn.JsonPath.string_at("$.plasmid_label"),
                    "primer_json": sfn.JsonPath.string_at("$.primer_json"),
                    "region_label": sfn.JsonPath.string_at("$.region_label"),
                    "sgRNA_primer_json": sfn.JsonPath.string_at("$.sgRNA_primer_json"),
                    "ccdb_primer_json": sfn.JsonPath.string_at("$.ccdb_primer_json"),
                    "sgRNA_region_label": sfn.JsonPath.string_at("$.sgRNA_region_label"),
                    "ccdb_region_label": sfn.JsonPath.string_at("$.ccdb_region_label"),
                    "enzyme": sfn.JsonPath.string_at("$.enzyme"),
                    "UHA_ARGS": sfn.JsonPath.string_at("$.UHA_ARGS"),
                    "SEQ_ALTERED_ARGS": sfn.JsonPath.string_at("$.SEQ_ALTERED_ARGS"),
                    "DHA_ARGS": sfn.JsonPath.string_at("$.DHA_ARGS"),
                    "UP_SGRNA_ARGS": sfn.JsonPath.string_at("$.UP_SGRNA_ARGS"),
                    "DOWN_SGRNA_ARGS": sfn.JsonPath.string_at("$.DOWN_SGRNA_ARGS"),
                    "PLASMID_Q_ARGS": sfn.JsonPath.string_at("$.PLASMID_Q_ARGS"),
                    "GENOME_Q_ARGS": sfn.JsonPath.string_at("$.GENOME_Q_ARGS"),
                    "sgRNA_result": sfn.JsonPath.string_at("$.sgRNA_result"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                }),
                result_path="$.Result.edit"
            )
        

        edit_both_task = sfn_tasks.LambdaInvoke(
                self,
                "run edit both sgRNA primer",
                lambda_function = TargetLambda.get_lambda_functions("editor_sequence_design"),
                payload= sfn.TaskInput.from_object({
                    "scene": sfn.JsonPath.string_at("$.scene"),
                    "chopchop_jobid": sfn.JsonPath.string_at("$.chopchop_jobid"),
                    "one_plasmid_file_path": sfn.JsonPath.string_at("$.one_plasmid_file_path"),
                    "no_ccdb_plasmid": sfn.JsonPath.string_at("$.no_ccdb_plasmid"),
                    "no_sgRNA_plasmid": sfn.JsonPath.string_at("$.no_sgRNA_plasmid"),
                    "uha_dha_config": sfn.JsonPath.string_at("$.uha_dha_config"),
                    "plasmid_label": sfn.JsonPath.string_at("$.plasmid_label"),
                    "primer_json": sfn.JsonPath.string_at("$.primer_json"),
                    "region_label": sfn.JsonPath.string_at("$.region_label"),
                    "sgRNA_primer_json": sfn.JsonPath.string_at("$.sgRNA_primer_json"),
                    "ccdb_primer_json": sfn.JsonPath.string_at("$.ccdb_primer_json"),
                    "sgRNA_region_label": sfn.JsonPath.string_at("$.sgRNA_region_label"),
                    "ccdb_region_label": sfn.JsonPath.string_at("$.ccdb_region_label"),
                    "enzyme": sfn.JsonPath.string_at("$.enzyme"),
                    "UHA_ARGS": sfn.JsonPath.string_at("$.UHA_ARGS"),
                    "SEQ_ALTERED_ARGS": sfn.JsonPath.string_at("$.SEQ_ALTERED_ARGS"),
                    "DHA_ARGS": sfn.JsonPath.string_at("$.DHA_ARGS"),
                    "UP_SGRNA_ARGS": sfn.JsonPath.string_at("$.UP_SGRNA_ARGS"),
                    "DOWN_SGRNA_ARGS": sfn.JsonPath.string_at("$.DOWN_SGRNA_ARGS"),
                    "PLASMID_Q_ARGS": sfn.JsonPath.string_at("$.PLASMID_Q_ARGS"),
                    "GENOME_Q_ARGS": sfn.JsonPath.string_at("$.GENOME_Q_ARGS"),
                    "sgRNA_result": sfn.JsonPath.string_at("$.sgRNA_result"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                }),
                result_path="$.Result.edit"
            )
        edit_job_finish = sfn_tasks.LambdaInvoke(
                self,
                "edit job finished?",
                lambda_function = TargetLambda.get_lambda_functions("job_status"),
                payload= sfn.TaskInput.from_object({
                    "result": sfn.JsonPath.string_at("$.Result"),
                    "jobid": sfn.JsonPath.string_at("$.jobid"),
                    
                }),
                result_path="$.Result.job_status"
            )
        
        edit_dp_task.next(edit_only_task).next(edit_job_finish)
        edit_both_task.next(edit_job_finish)
        # chain
        edit_chain = sfn.Chain.start(sfn.Choice(self, 'only or both?')
                  .when(sfn.Condition.string_equals('$.scene', 'only_primer'), edit_dp_task)
                  .when(sfn.Condition.string_equals('$.scene', 'both_sgRNA_primer'), edit_both_task))
                
        # statemachine
        edit_statemachine = sfn.StateMachine(
            self,
            "edit",
            definition=edit_chain
        )

        self.step_functions["edit"] = edit_statemachine
    def get_step_functions(self,name):
        return self.step_functions[name]
