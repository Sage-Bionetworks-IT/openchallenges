import aws_cdk as cdk

from aws_cdk import aws_s3 as s3

from constructs import Construct


class BucketStack(cdk.Stack):
    """
    Openchallenge Buckets
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------------------
        # create a S3 bucket
        # -------------------
        self.openchallenges_img_bucket = s3.Bucket(
            self,
            "ImageBucket",
            # TODO: do we need specific bucket name?
            # bucket_name="openchallenges-img",    # name is unique within a region
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        )
        cdk.CfnOutput(
            self,
            "ImageBucketArn",
            value=self.openchallenges_img_bucket.bucket_arn,
        )
        cdk.CfnOutput(
            self,
            "ImageBucketName",
            value=self.openchallenges_img_bucket.bucket_name,
        )
