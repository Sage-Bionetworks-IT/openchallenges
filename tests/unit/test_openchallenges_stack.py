import aws_cdk as core
import aws_cdk.assertions as assertions

from openchallenges.service_stack import ServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in openchallenges/openchallenges_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ServiceStack(app, "openchallenges")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
