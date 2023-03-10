#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:29:03
LastEditors: wangruoyu
LastEditTime: 2023-03-09 03:05:29
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/apigateway_construct.py
'''
import os
import json
import configparser
from aws_cdk import (
    aws_iam as iam,
    aws_apigateway as apigw,
)
from constructs import Construct

class APIConstruct(Construct):

    def read_config(self,part,name):
        """
        :part: which part ["config","url"]
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

    def __init__(self,scope:Construct,id:str,TargetDdb="default",TargetSqs="default",TargetLambda="default",TargetSfn="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self._method_arns = []
        
        # api role
        self.api_role = iam.Role(
            self,
            "api_role",
            assumed_by = iam.ServicePrincipal(
                "apigateway.amazonaws.com"
            )
        )

        # api gateway endpoint
        self._api = apigw.RestApi(
            self, 
            'chopchop-crispr-'+Stage
        )

        need_lambda_proxy = True
        # resouce API
        entity_api = self._api.root.add_resource('api')
        entity_chopchop = entity_api.add_resource('chopchop')
        # post
        chopchop_post_integration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('job_manager'),
            proxy=need_lambda_proxy,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )
        chopchop_post_method = entity_chopchop.add_method(
            'POST',
            chopchop_post_integration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ]
        )
        self._method_arns.append(
            chopchop_post_method.method_arn
        )
        # cors
        self.add_cors_options(entity_chopchop)
        
        # edit
        entity_edit = entity_api.add_resource('edit')
        # post
        edit_post_integration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('job_manager'),
            proxy=need_lambda_proxy,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )
        edit_post_method = entity_edit.add_method(
            'POST',
            edit_post_integration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ]
        )
        self._method_arns.append(
            edit_post_method.method_arn
        )
        # cors
        self.add_cors_options(entity_edit)
        
        # jobs
        entity_jobs = entity_api.add_resource('jobs')
        # post
        jobs_post_integration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('jobs'),
            proxy=False,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )
        jobs_post_method = entity_jobs.add_method(
            'POST',
            jobs_post_integration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ]
        )
        self._method_arns.append(
            jobs_post_method.method_arn
        )
        # cors
        self.add_cors_options(entity_jobs)

    def get_method_arns(self):
        return self._method_arns

    ## add CORS to api
    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method(
            'OPTIONS',
            apigw.MockIntegration(
                integration_responses=[
                    {
                        'statusCode': '200',
                        'responseParameters':{
                            'method.response.header.Access-Control-Allow-Headers':"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                            'method.response.header.Access-Control-Allow-Origin':"'*'",
                            'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'"
                        }
                    }
                ],
                passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={"application/json":"{\"statusCode\":200}"}
            ),
            method_responses=[
                {
                    'statusCode': '200',
                    'responseParameters':{
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                }
            ]
        )
