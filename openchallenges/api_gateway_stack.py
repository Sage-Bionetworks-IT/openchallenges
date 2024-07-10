import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_apigatewayv2 as apigwv2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_apigatewayv2_integrations as apigwv2_integrations
)

from constructs import Construct

ALB_HTTP_LISTENER_PORT = 80
ALB_HTTPS_LISTENER_PORT = 443
# manually created cert
CERTIFICATE_ARN = "arn:aws:acm:us-east-1:804034162148:certificate/76ed5a71-4aa8-4cc1-9db6-aa7a322ec077"

class ApiGatewayStack(cdk.Stack):
    """
      API Gateway
    """
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, fargate_service: ecs.FargateService,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        alb = elbv2.ApplicationLoadBalancer(self, "AppLoadBalancer", vpc=vpc, internet_facing=True)
        cdk.CfnOutput(self, "Dns", value=alb.load_balancer_dns_name)
        listener = alb.add_listener("listener", open=True,
                                    protocol=elbv2.ApplicationProtocol.HTTP,
                                   port=80
                                    )
        listener.add_targets("target", protocol=elbv2.ApplicationProtocol.HTTP,
                             port=80,
                             targets=[fargate_service]
                           )
        default_integration = apigwv2_integrations.HttpAlbIntegration("DefaultIntegration", listener)
        http_api = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                                   default_integration=default_integration)
        cdk.CfnOutput(self,"ApiEndpoint", value=http_api.api_endpoint)
        cdk.CfnOutput(self,"ApiUrl", value=http_api.url)
