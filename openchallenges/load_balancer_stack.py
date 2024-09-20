import aws_cdk as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)

from constructs import Construct


class LoadBalancerStack(cdk.Stack):
    """
    API Gateway to allow access to ECS app from the internet
    """

    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alb = elbv2.ApplicationLoadBalancer(
            self, "AppLoadBalancer", vpc=vpc, internet_facing=True
        )
        cdk.CfnOutput(self, "dns", value=self.alb.load_balancer_dns_name)
