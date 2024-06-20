import aws_cdk as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_certificatemanager as acm
)

from constructs import Construct

from openchallenges.service_props import (
    ALB_HTTP_LISTENER_PORT,
    ALB_HTTPS_LISTENER_PORT,
    CERTIFICATE_ARN
)

class NetworkStack(cdk.Stack):
    """
      Openchallenge Network
    """
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------------------
        # create a VPC
        # -------------------
        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.255.91.0/24")
        )

        # # -------------------
        # # ACM Certificate for HTTPS
        # # -------------------
        # self.cert = acm.Certificate.from_certificate_arn(
        #     self,
        #     "Cert",
        #     certificate_arn=CERTIFICATE_ARN
        # )
        #
        # # -------------------
        # # App load balancer for https endpoint
        # # -------------------
        # self.alb = elbv2.ApplicationLoadBalancer(
        #     self,
        #     "Alb",
        #     vpc=self.vpc,
        #     internet_facing=True
        # )
        # cdk.CfnOutput(
        #     self,
        #     "Dns",
        #     value=self.alb.load_balancer_dns_name
        # )
        # self.https_listener = self.alb.add_listener(
        #     "HttpsListener",
        #     port=ALB_HTTPS_LISTENER_PORT,
        #     open=True,
        #     ssl_policy=elbv2.SslPolicy.RECOMMENDED,
        #     certificates=[self.cert]
        # )
        # self.https_listener.add_action(
        #     "HttpsListenerResponse",
        #     action=elbv2.ListenerAction.fixed_response(
        #         200,
        #         content_type="text/plain",
        #         message_body="OK"
        #     )
        # )
        # self.http_listener = self.alb.add_listener(
        #     "HttpListener",
        #     port=ALB_HTTP_LISTENER_PORT,
        #     open=True
        # )
        # self.http_listener.add_action(
        #     "HttpListenerRedirect",
        #     action=elbv2.ListenerAction.redirect(
        #         port="443",
        #         protocol="HTTPS",
        #         permanent=True
        #     )
        # )

