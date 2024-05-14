import aws_cdk as cdk

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_route53_targets as targets,
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
            max_azs=2
        )

        # -------------------
        # ACM Certificate for HTTPS
        # -------------------
        self.cert = acm.Certificate.from_certificate_arn(
            self,
            "Cert",
            certificate_arn=CERTIFICATE_ARN
        )

        # -------------------
        # App load balancer for https endpoint
        # -------------------
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "Alb",
            vpc=self.vpc,
            internet_facing=True
        )
        cdk.CfnOutput(
            self,
            "Dns",
            value=self.alb.load_balancer_dns_name
        )
        self.https_listener = self.alb.add_listener(
            "HttpsListener",
            port=ALB_HTTPS_LISTENER_PORT,
            open=True,
            ssl_policy=elbv2.SslPolicy.RECOMMENDED,
            certificates=[self.cert]
        )
        self.https_listener.add_action(
            "HttpsListenerResponse",
            action=elbv2.ListenerAction.fixed_response(
                200,
                content_type="text/plain",
                message_body="OK"
            )
        )
        self.http_listener = self.alb.add_listener(
            "HttpListener",
            port=ALB_HTTP_LISTENER_PORT,
            open=True
        )
        self.http_listener.add_action(
            "HttpListenerRedirect",
            action=elbv2.ListenerAction.redirect(
                port="443",
                protocol="HTTPS",
                permanent=True
            )
        )

        # -------------------
        # Hosted Zone
        # -------------------
        # self.zone = route53.HostedZone(
        #     self,
        #     "Zone",
        # TODO: does service discovery handle setting up zone?
        #     zone_name="newinfra.openchallenges.io"
        # )
        # cdk.CfnOutput(
        #     self,
        #     "ZoneArn",
        #     value=self.zone.hosted_zone_arn
        # )
        # self.a_record = route53.ARecord(
        #     self,
        #     "AliasRecord",
        #     zone=self.zone,
        #     target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(self.alb))
        # )


        # -------------------
        # probably don't need this
        # -------------------
        # self.security_group = ec2.SecurityGroup(
        #     self,
        #     "security-group",
        #     vpc=self.vpc,
        # )
        # self.security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4("0.0.0.0/0"),
        #     connection=ec2.Port(
        #         protocol=ec2.Protocol.TCP,
        #         string_representation="host1",
        #         from_port=8000,
        #         to_port=8000
        #     )
        # )



