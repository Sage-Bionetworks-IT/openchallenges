import aws_cdk as cdk
from aws_cdk import (
    aws_scheduler_alpha as scheduler_alpha,
    aws_scheduler_targets_alpha as scheduler_targets,
)
from openchallenges.data_integration_lambda import DataIntegrationLambda
from openchallenges.data_integration_props import DataIntegrationProps
from constructs import Construct


class DataIntegrationStack(cdk.Stack):
    """
    Defines an AWS CDK stack for data integration.

    This stack sets up the resources required for scheduling and executing
    data integration tasks using AWS Lambda and EventBridge Scheduler.

    The stack includes:
    - A Lambda function for data integration.
    - An EventBridge Scheduler schedule to trigger the Lambda function.
    - An EventBridge Scheduler group for organizing schedules.

    Attributes:
        scope (Construct): The parent construct.
        id (str): The unique identifier for this stack.
        props (DataIntegrationProps): The properties for the data integration, including the schedule.
    """

    def __init__(
        self, scope: Construct, id: str, props: DataIntegrationProps, **kwargs
    ) -> None:
        """
        Initializes the DataIntegrationStack.

        Arguments:
            scope (Construct): The parent construct for this stack.
            id (str): The unique identifier for this stack.
            props (DataIntegrationProps): The properties required for data integration,
                including the schedule.
            **kwargs: Additional arguments passed to the base `cdk.Stack` class.
        """
        super().__init__(scope, id, **kwargs)

        data_integration_lambda = DataIntegrationLambda(self, f"${id}-lambda")

        target = scheduler_targets.LambdaInvoke(
            data_integration_lambda.lambda_function,
            input=scheduler_alpha.ScheduleTargetInput.from_object({}),
        )

        # Create a group for the schedule (maybe we want to add more schedules
        # to this group the future)
        schedule_group = scheduler_alpha.Group(
            self,
            f"${id}-schedule-group",
            group_name=f"${id}-schedule-group",
        )

        scheduler_alpha.Schedule(
            self,
            f"${id}-schedule",
            schedule=props.schedule,
            target=target,
            group=schedule_group,
            description=props.schedule_description,
        )
