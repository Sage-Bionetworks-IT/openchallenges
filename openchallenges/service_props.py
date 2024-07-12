class ServiceProps:
    """
    ECS service properties

    container_name: the name of the container
    container_port: the container application port
    container_memory: the container application memory
    container_location:
      supports "path://" for building container from local (i.e. path://docker/MyContainer)
      supports docker registry references (i.e. ghcr.io/sage-bionetworks/openchallenges-thumbor:latest)
    container_env_vars: a json dictionary of environment variables to pass into the container
      i.e. {"EnvA": "EnvValueA", "EnvB": "EnvValueB"}
    """

    def __init__(
        self,
        container_name: str,
        container_port: int,
        container_memory: int,
        container_location: str,
        container_env_vars: dict,
    ) -> None:
        self.container_name = container_name
        self.container_port = container_port
        self.container_memory = container_memory
        self.container_location = container_location
        self.container_env_vars = container_env_vars
