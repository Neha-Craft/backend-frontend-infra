from aws_cdk import Stack
from constructs import Construct
from .cons.ecs_construct import ECSConstruct

class IacInfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create ECS Cluster and related resources
        ecs_construct = ECSConstruct(self, "ECSConstruct")