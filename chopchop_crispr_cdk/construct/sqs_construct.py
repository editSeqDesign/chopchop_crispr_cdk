#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-23 08:21:08
LastEditors: wangruoyu
LastEditTime: 2023-02-23 08:21:25
Description: file content
FilePath: /chopchop_crispr_cdk/chopchop_crispr_cdk/construct/sqs_construct.py
'''
import os
import configparser


from aws_cdk import (
    aws_s3 as _s3,
    aws_sqs as sqs,
)

from constructs import Construct

class SqsConstruct(Construct):

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

        self.queues = {}

        # data preprocessing queue
        self.data_preprocessing_queue = sqs.Queue.from_queue_arn(
            self,
            "data_preprocessing",
            queue_arn= self.read_config(Stage,'data-preprocessing-queue-arn')
        )
        # chopchop queue
        self.chopchop_queue = sqs.Queue.from_queue_arn(
            self,
            "chopchop",
            queue_arn= self.read_config(Stage,'chopchop-queue-arn')
        )
        
        # edit_sequence_design queue
        self.edit_queue = sqs.Queue.from_queue_arn(
            self,
            "edit",
            queue_arn= self.read_config(Stage,'edit-queue-arn')
        )
        
        self.queues['data'] = self.data_preprocessing_queue
        self.queues['chopchop'] = self.chopchop_queue
        self.queues['edit'] = self.edit_queue
    
     
    def get_sqs_queues(self,name):
        return self.queues[name]