import os

from aws_cdk import (
    aws_s3 as _s3,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct
class IamConstruct(Construct):  
    def __init__(self,scope:Construct,id:str,TargetS3="default",TargetApiGateway="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        # user upload to s3  iam policy
        user_client_policy = iam.ManagedPolicy(self, "user-client",
            statements=[
                iam.PolicyStatement(
                    actions=["s3:GetObject","s3:PutObject","s3:DeleteObject"],
                    effect=iam.Effect.ALLOW,
                    resources=[TargetS3.get_s3_bucket('result').bucket_arn + "/public/*"]
                ),
                iam.PolicyStatement(
                    actions=["execute-api:Invoke"],
                    effect=iam.Effect.ALLOW,
                    resources=TargetApiGateway.get_method_arns()
                )
            ]
        )
        

        CfnOutput(
                self,
                "user client",
                value=user_client_policy.managed_policy_name
            )
