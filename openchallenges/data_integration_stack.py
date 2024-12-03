import aws_cdk as cdk
from openchallenges.data_integration_lambda import DataIntegrationLambda
from constructs import Construct


class DataIntegrationStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Instantiate the DataIntegrationLambda construct
        DataIntegrationLambda(self, "openchallenges-data-integration-lambda")
