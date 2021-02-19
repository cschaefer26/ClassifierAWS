from aws_cdk import core

from stacks.cicd_stack import CiCdStack
from stacks.networking_stack import NetworkingStack
from stacks.serving_stack import ServingStack

app = core.App()

shared_context = app.node.try_get_context('shared_context')

cdk_environment = core.Environment(
    region=shared_context['aws_region'],
    account=shared_context['aws_account'])

cicd = CiCdStack(scope=app,
                 id='classifier-cicd-stack',
                 env=cdk_environment,
                 shared_context=shared_context)

networking = NetworkingStack(app, 'classifier-networking-stack', env=cdk_environment)

serving = ServingStack(app,
                       id='classifier-serving-stack',
                       vpc=networking.vpc,
                       repository=cicd.ecr_repository,
                       env=cdk_environment,
                       shared_context=shared_context)

app.synth()
