from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class DataIntegrationLambda(Construct):
    """
    A CDK construct to define an AWS Lambda function for data integration.

    This construct creates an IAM role with the necessary permissions and a Docker-based
    Lambda function for handling data integration tasks.
    """

    def __init__(self, scope: Construct, id: str) -> None:
        """
        Builds the IAM role for the Lambda function.

        This role allows the Lambda function to execute basic AWS operations.

        Returns:
            iam.Role: The IAM role for the Lambda function.
        """
        super().__init__(scope, id)

        self.lambda_role = self._build_lambda_role()
        self.lambda_function = self._build_lambda_function(self.lambda_role)

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            f"{id}-LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name=("service-role/AWSLambdaBasicExecutionRole")
                )
            ],
        )

    def _build_lambda_function(self, role: iam.Role) -> lambda_.Function:
        """
        Builds the Docker-based AWS Lambda function.

        The Lambda function uses a Docker image built from a local directory.

        Args:
            role (iam.Role): The IAM role to associate with the Lambda function.

        Returns:
            _lambda.Function: The Docker-based AWS Lambda function.
        """
        return lambda_.DockerImageFunction(
            self,
            f"{id}-LambdaFunction",
            code=lambda_.DockerImageCode.from_image_asset(
                # Directory relative to where you execute cdk deploy contains a
                # Dockerfile with build instructions.
                directory="cdk_docker/data-integration-lambda"
            ),
            role=role,
            memory_size=128,
        )
