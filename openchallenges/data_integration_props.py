from dataclasses import dataclass
from aws_cdk.aws_scheduler_alpha import ScheduleExpression


@dataclass
class DataIntegrationProps:
    """
    Data integration properties.

    Attributes:
        schedule (ScheduleExpression): The schedule for triggering the data integration.
        schedule_description (str): The description of the schedule.
    """

    schedule: ScheduleExpression
    """The schedule for triggering the data integration."""

    schedule_description: str
    """The description of the schedule."""
