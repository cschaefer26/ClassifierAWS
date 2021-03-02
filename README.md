# Classifier AWS Deployment

This is a minimal implementation of a pipeline that deploys a simple text classifier into the AWS cloud
using the AWS Cloud Development Kit (CDK).

# Installation

Create a virtual environment and install the dependencies:

```
python -m venv .env
source .venv/bin/activate
pip install -r requirements.txt
```

You can test the installation by running:

```
PYTHONPATH=. pytest classifier/tests
```

# Before Deployment

- Make sure you have a valid AWS account and installed the command line tools  [CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) installed
- Create an AWS [IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) providing the credentials for creating resources.
- [Set up a CLI profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) with the IAM credentials and a default region (e.g. eu-central-1)
- Get your 12-digit IAM account id using `aws sts get-caller-identity`
- Create an AWS [GitHub connection](https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html) which allows AWS
  to clone your fork of this repo. The connection has a unique id (ARN).
- Open the file `infrastructure/app.py` and put the default region (e.g. eu-central-1) and account id and github connection ARN into the dictionary `shared_context`

# Deployment

Train a valid classifier:

```
PYTHONPATH=. python  classifier/train.py
```
The model will be saved under /tmp/classifier.pkl. When you trigger the deployment the pipeline will look for the model in the S3 bucket specified in the `shared_context` in the file `infrastructure/app.py`, thus you need to upload it there first.
Create a new bucket in the [AWS S3 console](https://s3.console.aws.amazon.com/s3) with the name `classifier-serving-model-bucket` and upload the classifier to the bucket.


Go to `infrastructure`, create a virtual environment and install the dependencies:

```
cd infrastructure
python -m venv .env
source .venv/bin/activate
pip install -r requirements.txt
```


Synthesize and deploy the CloudFormation template:
```
cd infrastructure
cdk synth
cdk deploy classifier-cicd-stack classifier-networking-stack classifier-serving-stack
```

Once the deployment is finished you can go to the AWS console and verify that the CodePipeline build went through. Logs are under CloudWatch/insights.
The classifier will is exposed to the internet via a LoadBalancer, whose DNS you can find under the [EC2 service](https://eu-central-1.console.aws.amazon.com/ec2): Go to   `Load balancers` and click on the running instance, the DNS will be displayed there. If you copy+paste the dns-address to your browser as: `dns-address/classify` then the input text field for the classifier should be displayed.

Make sure you destroy the resources once you don't need them anymore:

```
cdk destroy classifier-cicd-stack classifier-networking-stack classifier-serving-stack
```
