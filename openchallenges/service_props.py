
ALB_HTTP_LISTENER_PORT = 80
ALB_HTTPS_LISTENER_PORT = 443
# manually created cert
CERTIFICATE_ARN = "arn:aws:acm:us-east-1:804034162148:certificate/76ed5a71-4aa8-4cc1-9db6-aa7a322ec077"

class ServiceProps:
  """
  Shared stack properties
  """
  def __init__(self, container_name:str, container_port:int, container_memory:int, container_repo_url:str,
               container_env_vars:dict, web_path:str) -> None:
    self.container_name = container_name
    self.container_port = container_port
    self.container_memory = container_memory
    self.container_repo_url = container_repo_url
    self.container_env_vars = container_env_vars
    self.web_path = web_path
