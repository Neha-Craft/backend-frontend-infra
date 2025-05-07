import aws_cdk as core
import aws_cdk.assertions as assertions

from iac_infra.iac_infra_stack import IacInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in iac_infra/iac_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IacInfraStack(app, "iac-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
