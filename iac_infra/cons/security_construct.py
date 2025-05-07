from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam
)
from constructs import Construct

class SecurityConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create security group for the ECS tasks
        self.security_groups = []
        
        ecs_security_group = ec2.SecurityGroup(
            self, "PrimumAI-ECS-SG",
            vpc=vpc,
            description="Security group for ECS tasks",
            allow_all_outbound=True
        )

        ecs_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic"
        )

        self.security_groups.append(ecs_security_group)