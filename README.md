# Classifier AWS Deployment

This is a minimal implementation of a text classifier containing the code-infrastructure for deploying it to 
to the AWS cloud CDK.

# Installation

Create a virtual environment and install the dependencies

```
python3 -m venv .env
pip install -r requirements.txt
```

You can test the installation by running

```
PYTHONPATH=. pytest classifier/tests
```

# Before Deployment

- Make sure you have a valid AWS account and installed the command line tools  [CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) installed 
- Create an AWS [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) providing the credentials for creating resources.
- [Set up a CLI profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) with the IAM credentials and a default region (e.g. eu-central-1) 
- Get your 12-digit IAM iaccount id using aws sts `get-caller-identity` 
- Create an AWS [GitHub connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html) which allows AWS 
to clone your fork of this repo. The connection has a uniqe id (ARN).
- Put the default region (e.g. eu-central-1) and account id and github connection ARN into the `shared_context` dict `infrastructure/app.py`

# Deployment

Train a valid classifier

```
PYTHONPATH=. python  classifier/train.py
```
The model will be saved under /tmp/classifier.pkl. For deployment you need to upload it to a S3 bucket. Create a new bucket in the [AWS S3 console](https://s3.console.aws.amazon.com/s3) with the name `classifier-serving-model-bucket` and upload the classifier to the bucket.

Syntesize and deploy the CloudFormation template
```
cd infrastructure
cdk synth
cdk deploy classifier-cicd-stack, classifier-networking-stack, classifier-serving-stack
```

You can go to the AWS console and verify that the CodePipeline build went through. Logs are under CloudWatch/insights.
To access the front page of the classifier, first find the DNS under the [EC2 service](https://eu-central-1.console.aws.amazon.com/ec2), go to  
`LoadBalancers` and click on the running instance, the DNS will be displayed there. If you copy+paste the DNS address into the browser you should see the
rendered input text field for the classifier to try it out.