# Build and push to docker


## Build and Tag docker image
```
cd service-one
docker build -t service-one .
```

Tag for ECR
```
docker tag service-two:latest 804034162148.dkr.ecr.us-east-1.amazonaws.com/service-one
```

check builds with `docker images`

## Tag and Push to AWS ECR

### login to AWS and ECR 

login to AWS:
```
aws sso login --profile itsandbox-admin`
```

login to ECR:
```
aws ecr get-login-password --profile itsandbox-admin --region us-east-1 | docker login --username AWS --password-stdin 804034162148.dkr.ecr.us-east-1.amazonaws.com
```

if get-login-password doesn't work it might be due to
[issues with the ecr credentials helper](https://github.com/awslabs/amazon-ecr-credential-helper/issues/229).
try to install the latest version of the ecr credentials helper tools
```
go install github.com/awslabs/amazon-ecr-credential-helper/ecr-login/cli/docker-credential-ecr-login@latest
```


### create a repository and push container

create repository:
```
AWS_PROFILE=itsandbox-admin AWS_DEFAULT_REGION=us-east-1 aws ecr create-repository --repository-name service-one --region us-east-1
```

push container to ECR:
```
 AWS_PROFILE=itsandbox-admin AWS_DEFAULT_REGION=us-east-1 docker push 804034162148.dkr.ecr.us-east-1.amazonaws.com/service-one
```
