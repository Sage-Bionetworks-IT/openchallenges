import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_apigatewayv2 as apigwv2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_apigatewayv2_integrations as apigwv2_integrations
)

from constructs import Construct

class ApiGatewayStack(cdk.Stack):
    """
      API Gateway
    """
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, fargate_service: ecs.FargateService,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        alb = elbv2.ApplicationLoadBalancer(self, "AppLoadBalancer", vpc=vpc)
        listener = alb.add_listener("listener", port=80)
        listener.add_targets("target", port=8000,
                                targets= [
                                    fargate_service.load_balancer_target(
                                        container_name="apex",
                                        container_port=8000
                                    )
                                ],
                           )
        default_integration = apigwv2_integrations.HttpAlbIntegration("DefaultIntegration", listener)
        http_api = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                                   default_integration=default_integration)
        cdk.CfnOutput(self,"ApiEndpoint", value=http_api.api_endpoint)
