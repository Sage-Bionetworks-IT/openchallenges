import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    Size as size,
    aws_elasticloadbalancingv2 as elbv2
)

from constructs import Construct
from openchallenges.service_props import ServiceProps


class ServiceStack(cdk.Stack):
    """
    ECS Service stack
    """

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, cluster: ecs.Cluster,
                 props: ServiceProps, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS task with fargate
        self.task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            cpu=1024,
            memory_limit_mib=4096,
        )

        image = ecs.ContainerImage.from_registry(props.container_location)
        if "path://" in props.container_location:   # build container from source
            location = props.container_location.removeprefix("path://")
            image=ecs.ContainerImage.from_asset(location)

        port_mapping = ecs.PortMapping(
            name=props.container_name,
            container_port=props.container_port,
            protocol=ecs.Protocol.TCP,
        )

        if "Elasticsearch" in construct_id:
            port_mapping = ecs.PortMapping(
                name=props.container_name,
                container_port=props.container_port,
                app_protocol=ecs.AppProtocol.http
            )

        self.container = self.task_definition.add_container(
            props.container_name,
            image=image,
            memory_limit_mib=props.container_memory,
            environment=props.container_env_vars,
            port_mappings=[port_mapping],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f'{construct_id}',
                log_retention=logs.RetentionDays.FOUR_MONTHS
            )
        )

        self.security_group = ec2.SecurityGroup(
            self,
            "SecurityGroup",
            vpc=vpc
        )
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
            security_groups= ([self.security_group]),
            service_connect_configuration=ecs.ServiceConnectProps(
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix=f'{construct_id}'
                ),
                services=[
                    ecs.ServiceConnectService(
                        port_mapping_name=props.container_name,
                        port=props.container_port,
#                        dns_name=props.container_name
                    )
                ]
            )
        )

        # mount volume for DB
        if "MariaDb" in construct_id:
            self.volume = ecs.ServiceManagedVolume(
                self,
                "ServiceVolume",
                name=props.container_name,
                managed_ebs_volume=ecs.ServiceManagedEBSVolumeConfiguration(
                    size=size.gibibytes(30),
                    volume_type=ec2.EbsDeviceVolumeType.GP3,
                )
            )

            self.task_definition.add_volume(
                name=props.container_name,
                configured_at_launch=True
            )
            self.service.add_volume(self.volume)

            self.volume.mount_in(
                # should be mounted at openchallenges-mariadb:/data/db
                self.container,
                container_path="/data/db",
                read_only=False
            )


class ExternalServiceStack(ServiceStack):
    """
    We create a special service stack to allow putting the Load Balancer and the Service it is load balancing to
    in different stacks. The benefit of different stacks is that it makes maintaining the stacks easier.

    Due to the way AWS works, setting up a load balancer and ECS service in different stacks may cause cyclic references.
    https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/README.html#using-a-load-balancer-from-a-different-stack

    To work around this problem we use the "Split at listener" option from https://github.com/aws-samples/aws-cdk-examples
    """

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, cluster: ecs.Cluster, props: ServiceProps,
                 load_balancer:elbv2.ApplicationLoadBalancer, **kwargs) -> None:
        super().__init__(scope, construct_id, vpc, cluster, props, **kwargs)

        listener = elbv2.ApplicationListener(self,
                                             "Listener",
                                             load_balancer=load_balancer,
                                             port=80,
                                             open=True,
                                             protocol=elbv2.ApplicationProtocol.HTTP
                                             )
        listener.add_targets("target",
                             port=80,
                             protocol=elbv2.ApplicationProtocol.HTTP,
                             targets=[self.service]
                             )