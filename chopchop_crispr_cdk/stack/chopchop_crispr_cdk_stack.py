#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:29:38
LastEditors: wangruoyu
LastEditTime: 2023-03-09 02:54:31
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/stack/chopchop_crispr_cdk_stack.py
'''
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from chopchop_crispr_cdk.construct.lambda_construct import LambdaConstruct
from chopchop_crispr_cdk.construct.job_manager_lambda_construct import LambdaConstruct as JobLambdaConstruct
from chopchop_crispr_cdk.construct.s3_construct import S3Construct
from chopchop_crispr_cdk.construct.iam_construct import IamConstruct
from chopchop_crispr_cdk.construct.stepfunctions_construct import SfnConstruct
from chopchop_crispr_cdk.construct.dynamodb_construct import DynamodbConstruct
from chopchop_crispr_cdk.construct.apigateway_construct import APIConstruct

class ChopchopCrisprCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, Stage="default", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Definition of S3
        self.My_S3_Bucket = S3Construct(
            self,
            "s3-construct",
            Stage=Stage,
        )
        # Definiton of ddb table
        self.My_ddb = DynamodbConstruct(
            self,
            "ddb-construct",
            Stage=Stage,
        )
        # Defition of Lambda func
        self.My_Lambda_Func = LambdaConstruct(
            self,
            "lambda-construct",
            TargetS3 = self.My_S3_Bucket,
            TargetDdb= self.My_ddb,
            Stage=Stage,
        )

        # Defition of sfn
        self.My_Sfn = SfnConstruct(
            self,
            "sfn-construct",
            TargetLambda=self.My_Lambda_Func,
            Stage=Stage,
        )

        # Definition of job manager lambda
        self.My_job_lambda = JobLambdaConstruct(
            self,
            "job-lambda-construct",
            TargetSfn=self.My_Sfn,
            TargetDdb=self.My_ddb,
            Stage=Stage,
        )
        
        # Definition of api 
        self.My_api = APIConstruct(
            self,
            "api-construct",
            TargetLambda=self.My_job_lambda,
            Stage=Stage,
        )
        self.My_Iam = IamConstruct(
            self,
            "Iam-construct",
            TargetS3 = self.My_S3_Bucket
        )
