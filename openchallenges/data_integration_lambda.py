from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class DataIntegrationLambda(Construct):

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.lambda_role = self._build_lambda_role()
        self.lambda_function = self._build_lambda_function(self.lambda_role)

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name=("service-role/AWSLambdaBasicExecutionRole")
                )
            ],
        )

    # Create the Lambda function using a GHCR image
    def _build_lambda_function(self, role: iam.Role) -> _lambda.Function:
        return _lambda.DockerImageFunction(
            self,
            "LambdaFunction",
            code=_lambda.DockerImageCode.from_image_asset(
                # Directory relative to where you execute cdk deploy contains a
                # Dockerfile with build instructions.
                directory="cdk_docker/data_integration_lambda"
            ),
            role=role,
            memory_size=128,
            architecture=_lambda.Architecture.X86_64,
        )
