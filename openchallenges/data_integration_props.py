from dataclasses import dataclass
from aws_cdk.aws_scheduler_alpha import ScheduleExpression


@dataclass
class DataIntegrationProps:
    """
    Data integration properties
    """

    schedule: ScheduleExpression
