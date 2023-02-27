#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:29:03
LastEditors: wangruoyu
LastEditTime: 2023-02-16 05:29:22
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
            'chopchop-crispr'+Stage
        )


        # resouce API
        entity_api = self._api.root.add_resource('api')