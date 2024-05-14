import aws_cdk as cdk

from aws_cdk import (
    aws_certificatemanager as acm
)

from constructs import Construct

class CertStack(cdk.Stack):
    """
      create certificates which need to be done after creating a hosted zone
    """
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cert = acm.Certificate(
            self, "Certificate",
            domain_name=self.zone.zone_name,
            certificate_name="new-infra-openchallenges",  # Optionally provide an certificate name
            validation=acm.CertificateValidation.from_dns(self.zone)
        )
        cdk.CfnOutput(
            self,
            "cert-arn",
            value=self.cert.certificate_arn
        )
