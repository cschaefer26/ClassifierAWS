from typing import Dict

from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_codepipeline as pipeline,
    aws_codebuild as build,
    aws_codepipeline_actions as actions
)
from aws_cdk.aws_s3 import LifecycleRule


class CiCdStack(core.Stack):

    def __init__(self,
                 scope: core.Construct, id: str,
                 shared_context: Dict[str, str],
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.pipeline_id = f'{id}-cicd-stack'

        artifact_bucket = s3.Bucket(
            self, id=f'{id}-artifacts-bucket',
            removal_policy=core.RemovalPolicy.RETAIN,
            encryption=s3.BucketEncryption.KMS_MANAGED,
            versioned=False,
            lifecycle_rules=[
                LifecycleRule(expiration=core.Duration.days(2))
            ]
        )

        classifier_pipeline = pipeline.Pipeline(
            scope=self,
            id=f'{id}-pipeline',
            artifact_bucket=artifact_bucket,
            pipeline_name=self.pipeline_id,
            restart_execution_on_update=True,
        )

        source_output = pipeline.Artifact()

        classifier_pipeline.add_stage(
            stage_name='GithubSources',
            actions=[
                actions.BitBucketSourceAction(
                    connection_arn=shared_context['github_connection_arn'],
                    owner=shared_context['github_owner'],
                    repo=shared_context['github_repo'],
                    action_name='SourceCodeRepo',
                    branch='master',
                    output=source_output,
                )
            ])

        self.ecr_repository = ecr.Repository(scope=self,  id=f'{id}-ecr-repo')
        self.ecr_repository.add_lifecycle_rule(max_image_age=core.Duration.days(7))

        build_project = build.PipelineProject(
            self,
            id=f'{id}-build-project',
            project_name=f'ClassifierBuildProject',
            description=f'Build project for the classifier',
            environment=build.BuildEnvironment(build_image=build.LinuxBuildImage.STANDARD_3_0,
                                               privileged=True,
                                               compute_type=build.ComputeType.MEDIUM),
            environment_variables={
                'REPOSITORY_URI': build.BuildEnvironmentVariable(value=self.ecr_repository.repository_uri),
            },
            timeout=core.Duration.minutes(15),
            cache=build.Cache.bucket(artifact_bucket, prefix=f'codebuild-cache'),
            build_spec=build.BuildSpec.from_source_filename('buildspec.yml'),
        )

        build_project.add_to_role_policy(iam.PolicyStatement(
            actions=[
                'codebuild:CreateReportGroup',
                'codebuild:CreateReport',
                'codebuild:BatchPutTestCases',
                'codebuild:UpdateReport'
            ],
            resources=['*']
        ))

        self.ecr_repository.grant_pull_push(build_project)

        build_output = pipeline.Artifact()

        classifier_pipeline.add_stage(stage_name='BuildStage',
                                actions=[
                                    actions.CodeBuildAction(
                                        action_name='CodeBuildProjectAction',
                                        input=source_output,
                                        outputs=[build_output],
                                        project=build_project,
                                        type=actions.CodeBuildActionType.BUILD,
                                        run_order=1)]
                                )