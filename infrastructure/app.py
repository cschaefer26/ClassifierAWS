#!/usr/bin/env python3

from aws_cdk import (
    core
)

from stacks.cicd_stack import CiCdStack
from stacks.networking_stack import NetworkingStack
from stacks.serving_stack import ServingStack

shared_context = {'model_bucket_name': 'classifier-serving-model-bucket',
                  'aws_region': 'eu-central-1',
                  'aws_account': '***REMOVED***',
                  'port': 80,
                  'github_connection_arn': 'arn:aws:codestar-connections:eu-central-1:***REMOVED***:connection/98ebc764-190a-41f7-bed0-692237072a5f'}

cdk_environment = core.Environment(
    region=shared_context['aws_region'],
    account=shared_context['aws_account'])

app = core.App()

cicd = CiCdStack(scope=app,
                 id='classifier-cicd-stack',
                 env=cdk_environment,
                 github_connection_arn=shared_context['github_connection_arn'])

networking = NetworkingStack(app, 'classifier-networking-stack', env=cdk_environment)

serving = ServingStack(app,
                       id='classifier-serving-stack',
                       vpc=networking.vpc,
                       repository=cicd.ecr_repository,
                       env=cdk_environment,
                       shared_context=shared_context)


app.synth()
