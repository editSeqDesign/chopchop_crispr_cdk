import aws_cdk as core
import aws_cdk.assertions as assertions

from chopchop_crispr_cdk.chopchop_crispr_cdk_stack import ChopchopCrisprCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in chopchop_crispr_cdk/chopchop_crispr_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ChopchopCrisprCdkStack(app, "chopchop-crispr-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
