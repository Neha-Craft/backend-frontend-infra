from aws_cdk import (
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from constructs import Construct

class ApiGatewayConstruct(Construct):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, ecs_service, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC Link for the API Gateway
        vpc_link = apigateway.VpcLink(
            self, "PrimumAI-VPCLink",
            targets=[ecs_service.load_balancer]
        )

        # Create API Gateway
        self.api_gateway = apigateway.RestApi(
            self, "PrimumAI-API",
            rest_api_name="PrimumAI Backend API",
            description="API Gateway for PrimumAI Backend"
        )

        # Create integration
        integration = apigateway.Integration(
            type=apigateway.IntegrationType.HTTP_PROXY,
            integration_http_method="ANY",
            options=apigateway.IntegrationOptions(
                connection_type=apigateway.ConnectionType.VPC_LINK,
                vpc_link=vpc_link
            )
        )

        # Add proxy resource
        self.api_gateway.root.add_proxy(
            default_integration=integration,
            any_method=True
        )