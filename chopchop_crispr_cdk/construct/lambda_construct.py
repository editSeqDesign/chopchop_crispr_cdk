#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:24:52
LastEditors: wangruoyu
LastEditTime: 2023-02-16 06:11:06
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/lambda_construct.py
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

        # access to s3
        TargetS3.get_s3_bucket("result").grant_read_write(self.lambda_role)
        
        ####### layers #######
        # layer
        blastn_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "import existed blastn",
            layer_version_arn = self.read_config("layer","blastn")
        )
        
        biopython_pandas_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "import existed biopython pandas",
            layer_version_arn = self.read_config("layer","biopython-pandas")
        )
        ####### functions #######
        # data preprocessing 
        self.data_preprocessing = _lambda.Function(
            self,
            "data_preprocessing",
            runtime =_lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda/data_preprocessing'),
            role=self.lambda_role,
            handler="app.lambda_handler",
            timeout=Duration.seconds(30),
            layers=[blastn_layer,biopython_pandas_layer],
            # ephemeral_storage_size = Size.mebibytes(1024),
            memory_size=128,
            environment={
                "s3Result":TargetS3.get_s3_bucket('result').bucket_name,
            }
        )
        
        # editor sequence design
        self.editor_sequence_design = _lambda.Function(
            self,
            "editor_sequence_design",
            runtime =_lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda/editor_sequence_design'),
            role=self.lambda_role,
            handler="app.lambda_handler",
            timeout=Duration.seconds(30),
            layers=[blastn_layer,biopython_pandas_layer],
            memory_size=128,
            environment={
                "s3Result":TargetS3.get_s3_bucket('result').bucket_name,
            }
        )




         # chopchop
        # docker function
        self.chopchop = _lambda.DockerImageFunction(
            self,
            'DockerImageFunc',
            function_name='docker-chopchop',
            code=_lambda.DockerImageCode.from_image_asset( 
                directory=f'{os.path.abspath(os.path.join(os.getcwd()))}/lambda/chopchop', 
                file='logicDockerfile'
            ),
            role=self.lambda_role,
            memory_size=1024,
            timeout=Duration.seconds(60),
            environment={
                "s3Result":TargetS3.get_s3_bucket("result").bucket_name,
            }
        )

        self.lambda_functions["data_preprocessing"] = self.data_preprocessing
        self.lambda_functions["editor_sequence_design"] = self.editor_sequence_design
        self.lambda_functions["chopchop"] = self.chopchop

    def get_lambda_functions(self,name):
        return self.lambda_functions[name]
