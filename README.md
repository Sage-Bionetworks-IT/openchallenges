
# OpenChallenges AWS CDK app

AWS CDK app for deploying [OpenChallenges](https://openchallenges.io/).

# Perequisites

AWS CDK projects require some bootstrapping before synthesis or deployment.
Please review the [bootstapping documentation](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_bootstrap)
before development.

# Dev Container

This repository provides a [dev container](https://containers.dev/) that includes all the tools
required to develop this AWS CDK app.

## Opening the project inside its dev container

With VS Code:

1. Clone this repo
2. File > Open Folder...
3. A prompt should invite you to open the project inside the dev container. If not, open VS Code
    Command Palette and select "Dev Containers: Open Folder in Container..."

With GitHub Codespaces:

1. From the main page of this repository, click on the button "Code" > Codespaces > Click on the
   button "Create codespace"

That's it! You are now inside the dev container and have access to all the development tools.

# Development

All the development tools are provided when developing inside the dev container
(see above). These tools include Python, AWS CLI, AWS CDK CLI, etc. These tools
also include a Python virtual environment where all the Python packages needed
are already installed.

If you decide the develop outside of the dev container, some of the development
tools can be installed by running:

```console
./tools/setup.sh
```

Development requires the activation of the Python virtual environment:

```
$ source .venv/bin/activate
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


# Testing

## Static Analysis

As a pre-deployment step we syntatically validate the CDK json, yaml and
python files with [pre-commit](https://pre-commit.com).

Please install pre-commit, once installed the file validations will
automatically run on every commit.  Alternatively you can manually
execute the validations by running `pre-commit run --all-files`.

Verify CDK to Cloudformation conversion by running [cdk synth]:

```console
cdk synth
```

The Cloudformation output is saved to the `cdk.out` folder

## Unit Tests

Tests are available in the tests folder. Execute the following to run tests:

```
python -m pytest tests/ -s -v
```


# Environments

Deployment context is set in the [cdk.json](cdk.json) file.  An `ENV` environment variable must be
set to tell the CDK which environment's variables to use when synthesising or deploying the stacks.

Set an environment in cdk.json in `context` section of cdk.json:

```json
  "context": {
    "dev": {
        "VPC_CIDR": "10.255.92.0/24",
        "FQDN": "dev.openchallenges.io"
    },
    "prod": {
        "VPC_CIDR": "10.255.94.0/24",
        "FQDN": "prod.openchallenges.io"
    },
  }
```

For example, using the `prod` environment:

```console
ENV=prod cdk synth
```

# Certificates

Certificates to set up HTTPS connections should be created manually in AWS certificate manager.
This is not automated due to AWS requiring manual verification of the domain ownership.
Once created take the ARN of the certificate and add it to a context in cdk.json.

```json
  "context": {
    "dev": {
      "CERTIFICATE_ARN": "arn:aws:acm:us-east-1:XXXXXXXXX:certificate/76ed5a71-4aa8-4cc1-9db6-aa7a322ec077"
    }
  }
```

![ACM certificate](docs/acm-certificate.png)

# Secrets

Secrets can be stored in one of the following locations:
  * AWS SSM parameter store
  * Local context in [cdk.json](cdk.json) file

## Loading directly from cdk.json

Set secrets directly in cdk.json in `context` section of cdk.json:

```text
  "context": {
    "secrets": {
        "MARIADB_PASSWORD": "Dummy",
        "MARIADB_ROOT_PASSWORD": "Dummy",
        "GIT_HOST_KEY": "Host123",
        "GIT_PRIVATE_KEY": "-----BEGIN OPENSSH PRIVATE KEY-----\nDUMMY_GIT_PRIVATE_KEY\n-----END OPENSSH PRIVATE KEY-----",
        "AWS_LOADER_S3_ACCESS_KEY_ID": "AccessKey123",
        "AWS_LOADER_S3_SECRET_ACCESS_KEY": "SecretAccessKey123",
        "SECURITY_KEY": "SecurityKey123"
    }
  }
```

## Loading from ssm parameter store

Set secrets to the SSM parameter names in `context` section of cdk.json:

```text
  "context": {
    "secrets": {
        "MARIADB_PASSWORD": "/openchallenges/MARIADB_PASSWORD",
        "MARIADB_ROOT_PASSWORD": "/openchallenges/MARIADB_ROOT_PASSWORD",
        "GIT_HOST_KEY": "/openchallenges/GIT_HOST_KEY",
        "GIT_PRIVATE_KEY": "/openchallenges/GIT_PRIVATE_KEY",
        "AWS_LOADER_S3_ACCESS_KEY_ID": "/openchallenges/AWS_LOADER_S3_ACCESS_KEY_ID",
        "AWS_LOADER_S3_SECRET_ACCESS_KEY": "/openchallenges/AWS_LOADER_S3_SECRET_ACCESS_KEY",
        "SECURITY_KEY": "/openchallenges/SECURITY_KEY"
    }
  }
```

where the values of these KVs (e.g. `/openchallenges/MARIADB_PASSWORD`) refer to SSM parameters that
must be created manually.

![AWS secrets manager](docs/aws-parameter-store.png)

## Specify secret location

Set the `SECRETS` environment variable to specify the location where secrets should be loaded from.

Load secrets directly from cdk.json file:

```console
SECRETS=local cdk synth
```

Load secrets from AWS SSM parameter store:

```console
AWS_PROFILE=<your-aws-profile> AWS_DEFAULT_REGION=us-east-1 SECRETS=ssm cdk synth
```

> [!NOTE]
> Setting `SECRETS=ssm` requires access to an AWS account

## Override secrets from command line

The CDK CLI allows overriding context variables:

To load secrets directly from passed in values:

```console
SECRETS=local cdk --context  secrets='{"MARIADB_PASSWORD": "Dummy", "MARIADB_ROOT_PASSWORD": "Dummy", ..}' synth
```

To load secrets from SSM parameter store with overridden SSM parameter names:

```console
SECRETS=ssm cdk --context  "secrets"='{"MARIADB_PASSWORD": "/test/mariadb-root-pass", "MARIADB_ROOT_PASSWORD": "/test/mariadb-root-pass", ..}' synth
```

# Deployment

## Bootstrap

There are a few items that need to be manually bootstrapped before deploying the
OpenChallenges application.

* Add OC [secrets](#Secrets) to either the cdk.json or the AWS System Manager parameter store
* Create an [ACM certificate for the application](#Certificates) using the AWS Certificates Manager
* Add the Certificate ARN to the cdk.json
* Update references to the OC docker images in [app.py](app.py)
  (i.e. `ghcr.io/sage-bionetworks/openchallenges-xxx:<tag>`)
* (Optional) Update the `ServiceProps` objects in [app.py](app.py) with parameters specific to
  each container.

## Login with the AWS CLI

> [!NOTE]
> This and the following sections assume that you are working in the AWS account
> `org-sagebase-itsandbox` with the role `Developer` and that you are deploying
> to the `us-east-1` region. If this assumption is correct, you should be able
> to simply copy-paste the following commands, otherwise adapting the
> configuration should be straightforward.

Create the config file if it doesn't exist yet.

```console
mkdir ~/.aws && touch ~/.aws/config
```

As a Developer working in Sage IT Sandbox AWS account, add the following profile to the config file.

```ini
[profile itsandbox-dev]
sso_start_url = https://d-906769aa66.awsapps.com/start
sso_region = us-east-1
sso_account_id = XXXXXXXXX
sso_role_name = Developer
```

Login with the AWS CLI:

```console
aws --profile itsandbox-dev sso login
```


## Deploy

Deployment requires setting up an [AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html) then executing the
following command:

```console
AWS_PROFILE=itsandbox-dev AWS_DEFAULT_REGION=us-east-1 ENV=dev SECRETS=ssm cdk deploy --all
```

## Force new deployment

```console
AWS_PROFILE=itsandbox-dev AWS_DEFAULT_REGION=us-east-1 aws ecs update-service \
  --cluster <cluster-name> \
  --service <service-name> \
  --force-new-deployment
```

# Execute a command from a container running on ECS

Once a container has been deployed successfully it is accessible for debugging using the
[ECS execute-command](https://docs.aws.amazon.com/cli/latest/reference/ecs/execute-command.html)

Example to get an interactive shell run into a container:

```console
AWS_PROFILE=itsandbox-dev AWS_DEFAULT_REGION=us-east-1 aws ecs execute-command \
  --cluster OpenChallengesEcs-ClusterEB0386A7-BygXkQgSvdjY \
  --task a2916461f65747f390fd3e29f1b387d8 \
  --container openchallenges-mariadb \
  --command "/bin/sh" --interactive
```


# CI Workflow

This repo has been set up to use Github Actions CI to continously deploy the
OpenChallenges app.

The workflow for continuous integration:

* Create PR from the git dev branch
* PR is reviewed and approved
* PR is merged
* CI deploys changes to the dev environment (dev.openchallenges.io) in the org-sagebase-openchallenges-dev account.
* Changes are promoted (or merged) to the git stage branch.
* CI deploys changes to the staging environment (stage.openchallenges.io) in the org-sagebase-openchallenges-prod account.
* Changes are promoted (or merged) to the git prod branch.
* CI deploys changes to the prod environment (prod.openchallenges.io) in the org-sagebase-openchallenges-prod account.
