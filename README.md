# SBTi Temperature Alignment tool
This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop 
targets for official validation by the SBTi.

This tool can be used either as a standalone Python package or as an API.

## Structure
The folder structure for this project is as follows:

    .
    ├── .github                 # Github specific files (Github Actions workflows)
    ├── app                     # Flask app files for the API endpoints
    ├── docs                    # Documentation files (Sphinx)
    ├── config                  # Config files for the Docker container
    ├── SBTi                    # The main Python package for the temperature alignment tool
    └── test                    # Automated unit tests for the SBTi package (Nose2 tests)

## Installation
The SBTi package may be installed using PIP. If you'd like to install it locally use the following command:

```bash
pip install -e .
```

## Development
For development purposes, install the SBTi package using the following command:
```bash
pip install -e .[dev]
``` 

### Testing
Each class should be unit tested. The unit tests are written using the Nose2 framework.
The setup.py script should have already installed Nose2, so now you may run the tests as follows:
```bash
nose2 -v
```

## Deployment
The alignment tool can be used either as an standalone Python package or as an API.
The API can be deployed as a Docker container. To do this a Docker file is provided.
To start the docker container locally use the following command:
```bash
docker-compose up -d --build
```
The API should now be available at localhost on port 5000.

### Google Cloud Platform
TODO: document/link to documentation on how to deploy on GCP

### Amazon Web Services
These instructions assume that you've installed and configured the Amazon [AWS CLI tools](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and the [ECS CLI tools](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_Configuration.html) with an IAM account that has at least write access to ECS and EC2 and the capability of creating AIM roles.

1. Create a repository. 
```bash
aws ecr create-repository --repository-name sbti-ecs
```

*Output:*

```
{
    "repository": {
        "registryId": "aws_account_id",
        "repositoryName": "sbti-ecs",
        "repositoryArn": "arn:aws:ecr:region:aws_account_id:repository/sbti-ecs",
        "createdAt": 1505337806.0,
        "repositoryUri": "aws_account_id.dkr.ecr.region.amazonaws.com/sbti-ecs"
    }
}
```

2. Create your own AWS docker compose launch file
```bash
cp docker-compose_aws_example.yml docker-compose_aws.yml
```
2. Update the docker-compose_aws.yml file with the repository URI.
3. Build the docker image
```bash
docker-compose -f docker-compose_aws.yml build
```
4. Check if the image has indeed been build
```bash
docker image ls
```
5. Push the image to the repository
```bash
docker-compose -f docker-compose_aws.yml push
```
6. Configure the cluster. You can update the region and names as you see fit
```bash
ecs-cli configure --cluster sbti-ecs-cluster --region eu-central-1 --config-name sbti-ecs-conf --cfn-stack-name sbti-ecs-stack --default-launch-type ec2
```
7. Create a new key pair. The result of this command is a key. Store this safely as you can later use it to access your instance through SSH.
```bash
aws ec2 create-key-pair --key-name sbti
```
8. Create the instance that'll run the image. Here we used 1 server of type t2.medium. Change this as you see fit.
```bash
ecs-cli up --keypair sbti --capability-iam --size 1 --instance-type t2.medium --cluster-config sbti-ecs-conf
```
9. Update the server and make it run the docker image.
```bash
ecs-cli compose -f docker-compose_aws.yml up --cluster-config sbti-ecs-conf
```
10. Now that the instance is running we can't access it yet. That's because NGINX only listens to localhost. We need to change this to make sure it's accessible on the WWW.
11. Login to the Amazon AWS console
12. Go to the EC2 service
13. In the instance list find the instance running the Docker image
14. Copy the public IP address of the instance
15. In ```config/flask-site-nginx.conf``` update the server name to the public IP.
16. Now we need to rebuild and re-upload the image.

```bash
docker-compose -f docker-compose_aws.yml build --no-cache
docker-compose -f docker-compose_aws.yml push
ecs-cli compose -f docker-compose_aws.yml up --cluster-config sbti-ecs-conf --force-update
```
17. You should now be able to access the API.

> :warning: This will make the API publicly available on the world wide web! Please note that this API is not protected in any way. Therefore it's recommended to run your instance in a private subnet and only access it through there. Alternatively you can change the security group settings to only allow incoming connections from your local IP or company VPN.  

### Microsoft Azure
TODO: document/link to documentation on how to deploy on Azure