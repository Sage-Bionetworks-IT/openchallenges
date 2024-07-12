import aws_cdk as core
import aws_cdk.assertions as assertions

from openchallenges.network_stack import NetworkStack


# example tests. To run these tests, uncomment this file along with the example
# resource in openchallenges/openchallenges_stack.py
def test_sqs_queue_created():
    app = core.App()
    test_cidr = "10.99.99.0/24"
    network = NetworkStack(app, "TestStack", vpc_cidr=test_cidr)
    template = assertions.Template.from_stack(network)
    template.has_resource_properties("AWS::EC2::VPC", {"CidrBlock": test_cidr})
