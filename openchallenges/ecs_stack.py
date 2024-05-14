import aws_cdk as cdk

from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_servicediscovery as servicediscovery
)

from constructs import Construct

class EcsStack(cdk.Stack):
    """
      Openchallenge Buckets
    """
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------------------
        # ECS cluster
        # -------------------
        self.cluster = ecs.Cluster(
            self,
            "Cluster",
            vpc=vpc
        )

        # -------------------
        # Service discovery for ECS
        # -------------------
        self.service_namespace = servicediscovery.PrivateDnsNamespace(
            self,
            "ServiceNamespace",
            name="oc.org",
            vpc=vpc
        )
        self.service_map = servicediscovery.Service(
            self,
            "ServiceMap",
            namespace=self.service_namespace,
        )