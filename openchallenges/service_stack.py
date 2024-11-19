import aws_cdk as cdk

from aws_cdk import (
    Duration as duration,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    Size as size,
    aws_elasticloadbalancingv2 as elbv2,
    aws_certificatemanager as acm,
    aws_iam as iam,
)

from constructs import Construct
from openchallenges.service_props import ServiceProps

ALB_HTTP_LISTENER_PORT = 80
ALB_HTTPS_LISTENER_PORT = 443


class ServiceStack(cdk.Stack):
    """
    ECS Service stack
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        cluster: ecs.Cluster,
        props: ServiceProps,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # allow containers default task access and s3 bucket access
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogStream",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                    "logs:PutLogEvents",
                    "ssmmessages:CreateControlChannel",
                    "ssmmessages:CreateDataChannel",
                    "ssmmessages:OpenControlChannel",
                    "ssmmessages:OpenDataChannel",
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            )
        )

        # ECS task with fargate
        self.task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            cpu=1024,
            memory_limit_mib=4096,
            task_role=task_role,
        )

        image = ecs.ContainerImage.from_registry(props.container_location)
        if "path://" in props.container_location:  # build container from source
            location = props.container_location.removeprefix("path://")
            image = ecs.ContainerImage.from_asset(location)

        self.container = self.task_definition.add_container(
            props.container_name,
            image=image,
            memory_limit_mib=props.container_memory,
            environment=props.container_env_vars,
            port_mappings=[
                ecs.PortMapping(
                    name=props.container_name,
                    container_port=props.container_port,
                    protocol=ecs.Protocol.TCP,
                )
            ],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f"{construct_id}",
                log_retention=logs.RetentionDays.FOUR_MONTHS,
            ),
        )

        self.security_group = ec2.SecurityGroup(self, "SecurityGroup", vpc=vpc)
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(props.container_port),
        )

        # attach ECS task to ECS cluster
        self.service = ecs.FargateService(
            self,
            "Service",
            cluster=cluster,
            task_definition=self.task_definition,
            enable_execute_command=True,
            security_groups=([self.security_group]),
            service_connect_configuration=ecs.ServiceConnectProps(
                log_driver=ecs.LogDrivers.aws_logs(stream_prefix=f"{construct_id}"),
                services=[
                    ecs.ServiceConnectService(
                        port_mapping_name=props.container_name,
                        port=props.container_port,
                        dns_name=props.container_name,
                    )
                ],
            ),
        )

        # mount volumes
        for container_volume in props.container_volumes:
            service_volume = ecs.ServiceManagedVolume(
                self,
                "ContainerVolume",
                name=props.container_name,
                managed_ebs_volume=ecs.ServiceManagedEBSVolumeConfiguration(
                    size=size.gibibytes(container_volume.size),
                    volume_type=ec2.EbsDeviceVolumeType.GP3,
                ),
            )

            self.task_definition.add_volume(
                name=props.container_name, configured_at_launch=True
            )
            self.service.add_volume(service_volume)

            service_volume.mount_in(
                self.container,
                container_path=container_volume.path,
                read_only=container_volume.read_only,
            )


class LoadBalancedServiceStack(ServiceStack):
    """
    A special stack to create an ECS service fronted by a load balancer. This allows us to split up
    the ECS services and the load balancer into separate stacks.  It makes maintaining the stacks
    easier.  Unfortunately, due to the way AWS works, setting up a load balancer and ECS service
    in different stacks may cause cyclic references.
    https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/README.html#using-a-load-balancer-from-a-different-stack

    To work around this problem we use the "Split at listener" option from
    https://github.com/aws-samples/aws-cdk-examples
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        cluster: ecs.Cluster,
        props: ServiceProps,
        load_balancer: elbv2.ApplicationLoadBalancer,
        certificate_arn: str,
        health_check_path: str = "/",
        health_check_interval: int = 1,  # max is 5
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, vpc, cluster, props, **kwargs)

        # -------------------
        # ACM Certificate for HTTPS
        # -------------------
        self.cert = acm.Certificate.from_certificate_arn(
            self, "Cert", certificate_arn=certificate_arn
        )

        # -------------------------------
        # Setup https
        # -------------------------------
        https_listener = elbv2.ApplicationListener(
            self,
            "HttpsListener",
            load_balancer=load_balancer,
            port=ALB_HTTPS_LISTENER_PORT,
            open=True,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            certificates=[self.cert],
        )

        https_listener.add_targets(
            "HttpsTarget",
            port=props.container_port,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[self.service],
            health_check=elbv2.HealthCheck(
                path=health_check_path, interval=duration.minutes(health_check_interval)
            ),
        )

        # -------------------------------
        # redirect http to https
        # -------------------------------
        http_listener = elbv2.ApplicationListener(
            self,
            "HttpListener",
            load_balancer=load_balancer,
            port=ALB_HTTP_LISTENER_PORT,
            open=True,
            protocol=elbv2.ApplicationProtocol.HTTP,
        )

        http_listener.add_action(
            "HttpRedirect",
            action=elbv2.ListenerAction.redirect(
                port=str(ALB_HTTPS_LISTENER_PORT),
                protocol=(elbv2.ApplicationProtocol.HTTPS).value,
                permanent=True,
            ),
        )
