from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    aws_servicediscovery as servicediscovery
)

ALB_HTTP_LISTENER_PORT = 80
ALB_HTTPS_LISTENER_PORT = 443
# manually created cert
CERTIFICATE_ARN = "arn:aws:acm:us-east-1:804034162148:certificate/76ed5a71-4aa8-4cc1-9db6-aa7a322ec077"

class ServiceProps:
  """
  Shared stack properties
  """
  def __init__(self, cluster:ecs.Cluster, listener:elbv2.ApplicationListener, service_map:servicediscovery.Service,
               container_name:str,
               container_port:int, container_memory:int, container_repo_url:str, container_env_vars:dict,
               container_volume:str,
               is_public:bool,
               web_path:str, priority:str) -> None:
    self.cluster = cluster
    self.listener = listener
    self.service_map = service_map
    self.container_name = container_name
    self.container_port = container_port
    self.container_memory = container_memory
    self.container_repo_url = container_repo_url
    self.container_env_vars = container_env_vars
    self.container_volume = container_volume
    self.is_public = is_public
    self.web_path = web_path
    self.priority = priority