import aws_cdk as core
import aws_cdk.assertions as assertions

from openchallenges.app_stack import OpenchallengesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in openchallenges/openchallenges_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = OpenchallengesStack(app, "openchallenges")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
