import aws_cdk as cdk

from aws_cdk import aws_s3 as s3, aws_iam as iam

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

        # -------------------
        # IAM user with access to the openchallenges bucket
        # -------------------
        self.s3_user = iam.User(self, "ThumborUser", user_name="openchallenges-thumbor")
        # self.access_key = iam.AccessKey(self, "AccessKey", user=self.s3_user)
        # secret = ssm.Secret(
        #     self,
        #     "SecretAccessKey",
        #     secret_string_value=self.access_key.secret_access_key,
        # )
        # cdk.CfnOutput(self, "AccessKeyId", value=self.access_key.access_key_id)

        self.s3_user.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[self.openchallenges_img_bucket.bucket_arn],
                actions=["s3:ListBucket", "s3:GetObject*"],
            )
        )
        self.s3_user.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[f"{self.openchallenges_img_bucket.bucket_arn}/*"],
                actions=["s3:*Object"],
            )
        )
