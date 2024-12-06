from aws_cdk.aws_scheduler_alpha import ScheduleExpression


class DataIntegrationProps:
    """
    Data integration properties
    """

    def __init__(
        self,
        schedule: ScheduleExpression,
    ) -> None:
        self.schedule = schedule
