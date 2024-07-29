import aws_cdk as core
import aws_cdk.assertions as assertions

from openchallenges.network_stack import NetworkStack


def test_vpc_created():
    context = {
        "dev": {"VPC_CIDR": "10.255.92.0/24", "DNS_NAMESPACE": "openchallenges.io"}
    }

    app = core.App(context=context)
    env_context = app.node.try_get_context("dev")
    vpc_cidr = env_context["VPC_CIDR"]
    network = NetworkStack(app, "NetworkStack", vpc_cidr)
    template = assertions.Template.from_stack(network)
    template.has_resource_properties("AWS::EC2::VPC", {"CidrBlock": vpc_cidr})
