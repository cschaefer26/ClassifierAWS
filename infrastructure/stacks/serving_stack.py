import re
from typing import List

from aws_cdk.aws_ec2 import Port, Protocol
from aws_cdk.aws_ecs import PortMapping, HealthCheck
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationProtocol, IApplicationLoadBalancerTarget
from aws_cdk.aws_s3 import LifecycleRule
from aws_cdk import (
    aws_elasticloadbalancingv2 as elb,
    aws_sqs as sqs,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ssm as ssm,
    aws_sns as sns,
    aws_sns_subscriptions as snss,
    core
)


class ServingStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc,
                 repository: ecr.Repository, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = vpc

        self.ecs_cluster = ecs.Cluster(self,
                                       id=f'{id}-ecs',
                                       cluster_name='serving-ecs',
                                       vpc=self.vpc,
                                       container_insights=True)

        self.task_definition = ecs.FargateTaskDefinition(self,
                                                         id=f'{id}-ecs-task-definition',
                                                         memory_limit_mib=512, cpu=256)

        image = ecs.ContainerImage.from_ecr_repository(repository, 'latest')

        log_driver = ecs.AwsLogDriver(
            stream_prefix=id,
            log_retention=logs.RetentionDays.FIVE_DAYS
        )

        environment = {
            "QUEUE_URL": self.sqs_queue.queue_url,
            "QUEUE_ARN": self.sqs_queue.queue_arn,
            "QUEUE_NAME": self.sqs_queue.queue_name,
        }

        app_container = self.task_definition.add_container(id=f'{id}-container',
                                                           image=image,
                                                           logging=log_driver,
                                                           environment=environment)

        app_container.add_port_mappings(PortMapping(container_port=80, host_port=80))

        self.service = ecs.FargateService(self,
                                          id=f'{id}-fargate-service',
                                          assign_public_ip=True,
                                          cluster=self.ecs_cluster,
                                          desired_count=1,
                                          task_definition=self.task_definition)

        load_balancer = elb.ApplicationLoadBalancer(self,
                                                    id=f'{id}-LoadBalancer',
                                                    vpc=self.vpc,
                                                    internet_facing=True)

        load_balancer.connections.allow_from_any_ipv4(Port(protocol=Protocol.TCP,
                                                           string_representation='load_balancer_tcp_port',
                                                           from_port=80,
                                                           to_port=80))

        load_balancer.connections.allow_to_any_ipv4(Port(protocol=Protocol.TCP,
                                                         string_representation='load_balancer_tcp_port',
                                                         from_port=80,
                                                         to_port=80))

        listener = load_balancer.add_listener(id='Listener',
                                              port=80,
                                              protocol=ApplicationProtocol.HTTP)

        listener.add_targets(id='ServiceTarget',
                             port=80,
                             protocol=ApplicationProtocol.HTTP,
                             targets=[self.service])