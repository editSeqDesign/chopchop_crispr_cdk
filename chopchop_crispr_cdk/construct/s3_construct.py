#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:25:20
LastEditors: wangruoyu
LastEditTime: 2023-03-13 02:14:05
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/s3_construct.py
'''
import os
import configparser
from aws_cdk import (
    aws_s3 as _s3,
)
from constructs import Construct

class S3Construct(Construct):

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
        self.buckets = {}

        # import existed s3 bucket

        self.result_bucket = _s3.Bucket.from_bucket_name(
            self,
            'result',
            bucket_name = self.read_config(Stage,'result-bucket')
        )
        self.reference_bucket = _s3.Bucket.from_bucket_name(
            self,
            'reference',
            bucket_name = self.read_config(Stage,'reference-bucket')
        )

        self.buckets['result'] = self.result_bucket
        self.buckets['reference'] = self.reference_bucket
        
    
    def get_s3_bucket(self,name):
        return self.buckets[name]