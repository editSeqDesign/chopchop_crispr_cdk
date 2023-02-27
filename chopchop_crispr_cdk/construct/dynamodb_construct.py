#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-23 07:56:01
LastEditors: wangruoyu
LastEditTime: 2023-02-23 07:56:18
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/dynamodb_construct.py
'''
import os
import configparser

from aws_cdk import (
    aws_s3 as _s3,
    aws_dynamodb as ddb,
)

from constructs import Construct


class DynamodbConstruct(Construct):

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

    def __init__(self,scope:Construct,id:str,Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self.dynamodb_tables = {}


        # import result table
        self.result_table = ddb.Table.from_table_attributes(
            self,
            "import result table",
            table_name = self.read_config(Stage,'result-table'),
        )
        self.dynamodb_tables["result"] = self.result_table
    def get_dynamodb_tables(self,name):
        return self.dynamodb_tables[name]
