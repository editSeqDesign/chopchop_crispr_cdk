import os

from aws_cdk import (
    aws_s3 as _s3,
    aws_iam as iam
)
from constructs import Construct
class IamConstruct(Construct):  
    def __init__(self,scope:Construct,id:str,TargetS3="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        # auth user upload to s3  iam policy
        auth_user_upload_policy = iam.ManagedPolicy(self, "user-upload-s3-policy",
            statements=[
                iam.PolicyStatement(
                    actions=["s3:GetObject","s3:PutObject","s3:DeleteObject"],
                    effect=iam.Effect.ALLOW,
                    resources=[TargetS3.get_s3_bucket('result').bucket_arn + "/public/*"]
                )
            ]
        )
   