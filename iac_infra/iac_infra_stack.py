from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_apigateway as apigateway,
    CfnOutput
)
from constructs import Construct
from .cons.vpc_construct import VpcConstruct
from .cons.ecs_construct import EcsConstruct
from .cons.security_construct import SecurityConstruct
from .cons.apigateway_construct import ApiGatewayConstruct

class BackendInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with public and private subnets
        vpc = VpcConstruct(self, "VPC")

        # Create security groups and IAM roles
        security = SecurityConstruct(self, "Security", vpc=vpc.vpc)

        # Create ECS Cluster and Task Definitions
        ecs_cluster = EcsConstruct(self, "ECS", 
            vpc=vpc.vpc,
            security_groups=security.security_groups
        )

        # Create API Gateway
        api = ApiGatewayConstruct(self, "API",
            vpc=vpc.vpc,
            ecs_service=ecs_cluster.service
        )

        # Output the API Gateway URL
        CfnOutput(self, "ApiGatewayUrl",
            value=api.api_gateway.url,
            description="API Gateway URL"
        )