import aws_cdk as cdk
from aws_cdk import (
    CfnOutput,
    aws_events as events,
    aws_events_targets as event_target,
    aws_iam as iam,
    aws_scheduler as scheduler,
)
from openchallenges.data_integration_lambda import DataIntegrationLambda
from constructs import Construct


class DataIntegrationStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        data_integration_lambda = DataIntegrationLambda(self, "data-integration-lambda")

        event_bus = events.EventBus(self, "event-bus")

        event_rule = events.Rule(
            self,
            "event-rule",
            event_bus=event_bus,
            event_pattern=events.EventPattern(source=["scheduled.events"]),
        )

        # Set the event rule target to the lambda function
        event_rule.add_target(
            event_target.LambdaFunction(data_integration_lambda.lambda_function)
        )

        scheduler_role = iam.Role(
            self,
            "scheduler-role",
            assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
        )

        scheduler_events_policy = iam.PolicyStatement(
            actions=["events:PutEvents"],
            resources=[event_bus.event_bus_arn],
            effect=iam.Effect.ALLOW,
        )

        scheduler_role.add_to_policy(scheduler_events_policy)

        # Create a group for the schedule (maybe we want to add more schedules
        # to this group the future)
        schedule_group = scheduler.CfnScheduleGroup(
            self,
            "schedule-group",
            name="schedule-group",
        )

        schedule = scheduler.CfnSchedule(
            self,
            "schedule",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression="rate(5 minute)",
            group_name=schedule_group.name,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=event_bus.event_bus_arn,
                role_arn=scheduler_role.role_arn,
                event_bridge_parameters=scheduler.CfnSchedule.EventBridgeParametersProperty(
                    detail_type="ScheduleTriggered", source="scheduled.events"
                ),
            ),
        )

        # Output
        CfnOutput(self, "SCHEDULE_NAME", value=schedule.ref)
        CfnOutput(self, "EVENT_BUS_NAME", value=event_bus.event_bus_name)
        CfnOutput(
            self,
            "LAMBDA_FUNCTION_NAME",
            value=data_integration_lambda.lambda_function.function_name,
        )
