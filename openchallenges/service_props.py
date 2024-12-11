from dataclasses import dataclass
from typing import List

CONTAINER_LOCATION_PATH_ID = "path://"


@dataclass
class ContainerVolume:
    """
    Holds onto configuration for a volume used in the container.

    Attributes:
      path: The path on the container to mount the host volume at.
      size: The size of the volume in GiB.
      read_only: Container has read-only access to the volume, set to `false` for write access.
    """

    path: str
    size: int = 15
    read_only: bool = False


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
    container_volumes: List of `ContainerVolume` resources to mount into the container
    """

    def __init__(
        self,
        container_name: str,
        container_port: int,
        container_memory: int,
        container_location: str,
        container_env_vars: dict,
        container_volumes: List[ContainerVolume] = None,
    ) -> None:
        self.container_name = container_name
        self.container_port = container_port
        self.container_memory = container_memory
        if CONTAINER_LOCATION_PATH_ID in container_location:
            container_location = container_location.removeprefix(
                CONTAINER_LOCATION_PATH_ID
            )
        self.container_location = container_location
        self.container_env_vars = container_env_vars
        if container_volumes is None:
            self.container_volumes = []
        else:
            self.container_volumes = container_volumes
