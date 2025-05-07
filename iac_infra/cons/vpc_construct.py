from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm
)
from constructs import Construct

class VpcConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC with public and private subnets
        self.vpc = ec2.Vpc(self, "PrimumAI-VPC",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PrimumAI-Public-Subnet",  
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrimumAI-Private-Subnet", 
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ],
            nat_gateways=1
        )