from aws_cdk import (
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    Duration
)
from constructs import Construct

class EcsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, security_groups, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create ECS Cluster
        self.cluster = ecs.Cluster(self, "PrimumAI-ECS-Cluster",
            vpc=vpc
        )

        # Create Task Definition for auth-backend-service
        task_definition = ecs.FargateTaskDefinition(self, "PrimumAI-Backend-Task",
            memory_limit_mib=512,
            cpu=256
        )

        # Add ECR permissions to task execution role
        task_definition.add_to_execution_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                resources=["*"]
            )
        )

        # Add container to task definition
        container = task_definition.add_container("PrimumAI-Backend-Container",
            image=ecs.ContainerImage.from_registry("148761648660.dkr.ecr.ap-south-1.amazonaws.com/backend"),
            environment={
                "NODE_ENV": "production"
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="primumai-backend"
            )
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=80)
        )

        # Create Fargate Service with NLB
        self.service = ecs_patterns.NetworkLoadBalancedFargateService(self, "PrimumAI-Backend-Service",
            cluster=self.cluster,
            task_definition=task_definition,
            public_load_balancer=True,
            desired_count=2,
            security_groups=security_groups
        )

        # Configure TCP health check for NLB
        self.service.target_group.configure_health_check(
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5)
        )

        # Configure health check
        # self.service.target_group.configure_health_check(
        #     path="/health",
        #     healthy_http_codes="200",
        #     healthy_threshold_count=2,
        #     interval=Duration.seconds(30),
        #     timeout=Duration.seconds(5)
        # )
