#-*- coding:utf-8 -*-
'''
Author: wangruoyu, wangry@tib.cas.cn
Date: 2023-02-16 05:26:22
LastEditors: wangruoyu
LastEditTime: 2023-02-16 05:30:27
Description: file content
FilePath: /chopchop_crispr_cdk/app.py
'''
#!/usr/bin/env python3
import os

import aws_cdk as cdk

from chopchop_crispr_cdk.stack.chopchop_crispr_cdk_stack import ChopchopCrisprCdkStack

STAGE="prod"

ENV = {"account": os.environ["ACCOUNTID"], "region": os.environ["AWS_DEFAULT_REGION"]}

app = cdk.App()

# prod stack
ChopchopCrisprCdkStack(
    app, 
    "ChopchopCrisprCdkStack" + f"-{STAGE}",
    env=ENV,
    Stage=STAGE,
    )

app.synth()
