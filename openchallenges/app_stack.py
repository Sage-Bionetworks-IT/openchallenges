import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_logs as logs,
    Size as size,
)

from constructs import Construct
from openchallenges.service_props import ServiceProps
from openchallenges.service_props import (
    ALB_HTTP_LISTENER_PORT,
    ALB_HTTPS_LISTENER_PORT
)


class AppStack(cdk.Stack):
    """
    ECS task
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

        self.container = self.task_definition.add_container(
            props.container_name,
            # image=ecs.ContainerImage.from_asset(props.disk_path),  # build container from source
            image=ecs.ContainerImage.from_registry(props.container_repo_url),
            memory_limit_mib=props.container_memory,
            environment=props.container_env_vars,
            port_mappings=[
                ecs.PortMapping(
                    name=props.container_name,
                    container_port=props.container_port,
                    app_protocol=ecs.AppProtocol.http
                )
            ],
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
                description='Allow all inbound traffic'
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
                    )
                ]
            )
        )

        if construct_id=="OpenChallengesMariaDb":
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


        # this causes a bootstrap check failure [1] of [1]: max virtual memory areas
        #   vm.max_map_count [65530] is too low, increase to at least [262144]
        # if id=="elasticache":
        #     ulimit = ecs.Ulimit(
        #         name=ecs.UlimitName.MEMLOCK,
        #         hard_limit=-1,
        #         soft_limit=-1
        #
        #     )
        #     self.container.add_ulimits(ulimit)

        # expose container port to ALB HTTP port
        # if construct_id=="OpenChallengesApex":
        #     props.listener.add_targets(
        #         "ListenerTarget",
        #         priority=5,
        #         conditions=[
        #             elbv2.ListenerCondition.path_patterns(
        #                 [props.web_path]
        #             )
        #         ],
        #         port=ALB_HTTPS_LISTENER_PORT,
        #         targets= [
        #             self.service.load_balancer_target(
        #                 container_name=props.container_name,
        #                 container_port=props.container_port
        #             )
        #         ],
        #         health_check= {
        #             "interval": cdk.Duration.seconds(10),
        #             "path": props.web_path,
        #             "timeout": cdk.Duration.seconds(5),
        #         },
        #         deregistration_delay=cdk.Duration.seconds(10)
        #     )

