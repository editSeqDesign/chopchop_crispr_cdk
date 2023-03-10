#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:24:52
LastEditors: wangruoyu
LastEditTime: 2023-03-09 07:06:05
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/job_manager_lambda_construct.py
'''
import os
import configparser
from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_iam as iam,
    Duration,Size,
)

from constructs import Construct

class LambdaConstruct(Construct):
    def read_config(self,part,name):
        """
        :part: which part in conf, ["config","url"]
        :name: config name
        :return: config value
        """
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(path)
        conf= configparser.ConfigParser()
        conf.read(os.path.join(path, "construct/app.conf"))
        value = conf.get(part,name)
        print(value)
        return value
      
    def __init__(self,scope:Construct,id:str,TargetS3 = "default",TargetDdb="default",TargetSqs="default",TargetSfn="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self.lambda_functions = {}
        self.lambda_arns = []
        # lambda role
        self.lambda_role = iam.Role(
            self,
            "lambda-role",
            assumed_by = iam.ServicePrincipal(
                "lambda.amazonaws.com"
            )
        )
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['logs:CreateLogGroup','logs:CreateLogStream','logs:PutLogEvents'],
                resources=["*"]
            )
        )
        # sfn submit access
        TargetSfn.get_step_functions("chopchop").grant_start_execution(self.lambda_role)
        TargetSfn.get_step_functions("edit").grant_start_execution(self.lambda_role)
        
        # ddb access
        TargetDdb.get_dynamodb_tables('result').grant_full_access(self.lambda_role)
        
        ####### functions #######
        # job manager
        self.job_manager = _lambda.Function(
            self,
            "job_manager",
            runtime =_lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda/job_manager'),
            role=self.lambda_role,
            handler="app.lambda_handler",
            timeout=Duration.seconds(10),
            # ephemeral_storage_size = Size.mebibytes(1024),
            memory_size=128,
            environment={
                "ddbResult":TargetDdb.get_dynamodb_tables('result').table_name,
                "sfnChopchop":TargetSfn.get_step_functions('chopchop').state_machine_arn,
                "sfnEdit":TargetSfn.get_step_functions('edit').state_machine_arn,
            }
        )
        
        # jobs
        self.jobs = _lambda.Function(
            self,
            "jobs",
            runtime =_lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda/jobs'),
            role=self.lambda_role,
            handler="app.lambda_handler",
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "ddbResult":TargetDdb.get_dynamodb_tables('result').table_name,
            }
        )

        self.lambda_functions["job_manager"] = self.job_manager
        self.lambda_functions["jobs"] = self.jobs

    def get_lambda_functions(self,name):
        return self.lambda_functions[name]
