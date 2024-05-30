import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    Size as size,
    aws_elasticloadbalancingv2 as elbv2,
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

    def __init__(self, scope: Construct, construct_id: str, props: ServiceProps, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS task with fargate
        self.task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDef",
            cpu=1024,
            memory_limit_mib=4096
        )
        self.container = self.task_definition.add_container(
            props.container_name,
            # image=ecs.ContainerImage.from_asset(props.disk_path),
            image=ecs.ContainerImage.from_registry(props.container_repo_url),
            memory_limit_mib=props.container_memory,
            port_mappings=[
                ecs.PortMapping(
                    container_port=props.container_port
                )
            ],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f'{construct_id}',
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=size.mebibytes(25)
            ),
            environment=props.container_env_vars
        )

        # attach ECS task to ECS cluster
        self.service = ecs.FargateService(
            self,
            "Service",
            cluster=props.cluster,
            task_definition=self.task_definition,
            # volume_configuration=
        )

        self.service.associate_cloud_map_service(
            service=props.service_map
        )

        if id=="mariadb":
            self.volume = ecs.ServiceManagedVolume(
                self,
                f'{construct_id}-volume',
                name=f'{construct_id}-volume',
                managed_ebs_volume=ecs.ServiceManagedEBSVolumeConfiguration(
                    size=size.gibibytes(30),
                    volume_type=ec2.EbsDeviceVolumeType.GP3,
                )
            )

            self.volume.mount_in(
                # should be mounted at openchallenges-mariadb:/data/db
                self.container,
                container_path="/data/db",
                read_only=False
            )

            self.task_definition.add_volume(
                name=f'{construct_id}-volume',
                configured_at_launch=True
            )
            self.service.add_volume(self.volume)

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
        if props.is_public:
            props.listener.add_targets(
                "ListenerTarget",
                priority=props.priority,
                conditions=[
                    elbv2.ListenerCondition.path_patterns(
                        [props.web_path]
                    )
                ],
                port=ALB_HTTPS_LISTENER_PORT,
                targets= [
                    self.service.load_balancer_target(
                        container_name=props.container_name,
                        container_port=props.container_port
                    )
                ],
                health_check= {
                    "interval": cdk.Duration.seconds(10),
                    "path": props.web_path,
                    "timeout": cdk.Duration.seconds(5),
                },
                deregistration_delay=cdk.Duration.seconds(10)
            )

