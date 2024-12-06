import aws_cdk as cdk
from aws_cdk import (
    aws_scheduler_alpha as scheduler_alpha,
    aws_scheduler_targets_alpha as scheduler_targets,
)
from openchallenges.data_integration_lambda import DataIntegrationLambda
from openchallenges.data_integration_props import DataIntegrationProps
from constructs import Construct


class DataIntegrationStack(cdk.Stack):

    def __init__(
        self, scope: Construct, id: str, props: DataIntegrationProps, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        data_integration_lambda = DataIntegrationLambda(self, "data-integration-lambda")

        target = scheduler_targets.LambdaInvoke(
            data_integration_lambda.lambda_function,
            input=scheduler_alpha.ScheduleTargetInput.from_object({}),
        )

        # Create a group for the schedule (maybe we want to add more schedules
        # to this group the future)
        schedule_group = scheduler_alpha.Group(
            self,
            "group",
            group_name="schedule-group",
        )

        scheduler_alpha.Schedule(
            self,
            "schedule",
            schedule=props.schedule,
            target=target,
            group=schedule_group,
            description="This is a cron-based schedule that will run every 5 minutes",
        )
