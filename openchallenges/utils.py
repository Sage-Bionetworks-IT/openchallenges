import boto3
import aws_cdk as cdk

from botocore.exceptions import ClientError
from os import environ


def get_environment() -> str:
    """
    The `ENV` environment variable's value represents the deployment
    environment (dev, prod, etc..).  This method gets the `ENV`
    environment variable's value
    """
    VALID_ENVS = ["dev", "prod"]

    env_environment_var = environ.get("ENV")
    if env_environment_var is None:
        environment = "dev"  # default environment
    elif env_environment_var in VALID_ENVS:
        environment = env_environment_var
    else:
        valid_envs_str = ",".join(VALID_ENVS)
        raise SystemExit(
            f"Must set environment variable `ENV` to one of {valid_envs_str}"
        )

    return environment


def get_secrets_location() -> dict:
    """
    The application's secrets can be saved in two places, the AWS parameter store
    or directly in the cdk.json file as a `context` value.  This method returns
    information on the location where secrets are stored.
    * `local` - stored in cdk.json file
    * `ssm` - stored in AWS SSM parameter store
    """
    VALID_LOCATIONS = ["local", "ssm"]
    secrets_environment_var = environ.get("SECRETS")
    if secrets_environment_var is None:
        location = "local"  # default secrets location
    elif secrets_environment_var in VALID_LOCATIONS:
        location = secrets_environment_var
    else:
        valid_locations_str = ",".join(VALID_LOCATIONS)
        raise SystemExit(
            f"Must set environment variable `SECRETS` to one of {valid_locations_str}"
        )

    return location


def get_ssm_secrets(param_store_secret_refs: dict) -> dict:
    """
    Retrieve secrets from the AWS SSM parameter store.

    param_store_secret_refs is a dictionary that contains the key/ssm param name
    for each secret.

    Example param_store_secret_refs:
    {
        "MARIADB_PASSWORD": "/openchallenges/MARIADB_PASSWORD",
        "GIT_PRIVATE_KEY": "/openchallenges/GIT_PRIVATE_KEY"
    }

    Retrieve from SSM parameter store "/openchallenges/MARIADB_PASSWORD" and assign it to MARIADB_PASSWORD
    Retrieve from SSM parameter store "/openchallenges/GIT_PRIVATE_KEY" and assign it to GIT_PRIVATE_KEY

    Example returned value:
    {
        "MARIADB_PASSWORD": "123ABC"
        "GIT_PRIVATE_KEY": "-----BEGIN OPENSSH PRIVATE KEY-----123..ABC-----END OPENSSH PRIVATE KEY-----"
    }
    """
    ssm = boto3.client("ssm")
    secrets = {}
    for key, value in param_store_secret_refs.items():
        secret_name = key
        try:
            response = ssm.get_parameter(Name=value, WithDecryption=True)
            secret_value = response["Parameter"]["Value"]
            secrets[secret_name] = secret_value
        except ClientError as e:
            raise e

    return secrets


def get_secrets(app: cdk.App) -> dict:
    """
    Secrets can be stored in the following locations:
      1. Directly in the cdk.json file in a `secrets` context
      2. In the AWS SSM parameter store
    Retrieve secrets from one of those locations using the context value from the ENV
    environment value and from the cdk.json context value.
    """
    secrets_location = get_secrets_location()
    if secrets_location == "local":
        secrets = app.node.try_get_context("secrets")
    elif secrets_location == "ssm":
        param_store_secret_refs = app.node.try_get_context("secrets")
        secrets = get_ssm_secrets(param_store_secret_refs)

    return secrets
