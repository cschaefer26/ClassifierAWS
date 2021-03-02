from typing import Dict, Any

from aws_cdk import (
    aws_elasticloadbalancingv2 as elb,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    core
)
from aws_cdk.aws_ec2 import Port, Protocol
from aws_cdk.aws_ecs import PortMapping
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationProtocol


class ServingStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc: ec2.Vpc,
                 repository: ecr.Repository,
                 shared_context: Dict[str, Any],
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc

        self.model_bucket = s3.Bucket.from_bucket_name(scope=self,
                                                       id=f'{id}-model-bucket',
                                                       bucket_name=shared_context['model_bucket_name'])

        self.ecs_cluster = ecs.Cluster(self,
                                       id=f'{id}-ecs',
                                       cluster_name='serving-ecs',
                                       vpc=self.vpc,
                                       container_insights=True)

        self.task_definition = ecs.FargateTaskDefinition(self,
                                                         id=f'{id}-ecs-task-definition',
                                                         memory_limit_mib=shared_context['fargate_memory_limit_mb'],
                                                         cpu=shared_context['fargate_cpu_units'])

        self.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            actions=['s3:getObject'],
            effect=iam.Effect.ALLOW,
            resources=[self.model_bucket.bucket_arn, self.model_bucket.bucket_arn + '/*']
        ))

        image = ecs.ContainerImage.from_ecr_repository(repository, 'latest')

        log_driver = ecs.AwsLogDriver(
            stream_prefix=id,
            log_retention=logs.RetentionDays.FIVE_DAYS
        )

        environment = {
            'MODEL_BUCKET_NAME': shared_context['model_bucket_name']
        }

        app_container = self.task_definition.add_container(id=f'{id}-container',
                                                           image=image,
                                                           logging=log_driver,
                                                           environment=environment)

        app_container.add_port_mappings(PortMapping(container_port=shared_context['port'],
                                                    host_port=shared_context['port']))

        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(self,
                                                                          id=f'{id}-fargate-service',
                                                                          assign_public_ip=True,
                                                                          cluster=self.ecs_cluster,
                                                                          desired_count=1,
                                                                          task_definition=self.task_definition,
                                                                          open_listener=True,
                                                                          listener_port=shared_context['port'],
                                                                          target_protocol=ApplicationProtocol.HTTP)
