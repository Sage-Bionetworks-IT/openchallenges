


class ServiceProps:
  """
  Shared stack properties
  """
  def __init__(self, container_name:str, container_port:int, container_memory:int, container_location:str,
               container_env_vars:dict, web_path:str) -> None:
    self.container_name = container_name
    self.container_port = container_port
    self.container_memory = container_memory
    self.container_location = container_location
    self.container_env_vars = container_env_vars
    self.web_path = web_path
