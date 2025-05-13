from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    Stack,
    Duration,
    Size  
)
from constructs import Construct

class ECSConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id)

        
        self.vpc = ec2.Vpc.from_lookup(
            self, 
            "ExistingVPC",
            vpc_id="vpc-0dc1616c617e1236f"  
        )

        # Get existing subnets with explicit Availability Zones
        public_subnets = [
            ec2.Subnet.from_subnet_attributes(
                self,
                "PublicSubnetA",  
                availability_zone="eu-west-1a",
                subnet_id="subnet-03ba29a1f6c9783c8" 
            ),
            ec2.Subnet.from_subnet_attributes(
                self,
                "PublicSubnetB",  
                availability_zone="eu-west-1a",
                subnet_id="subnet-014ae1a5e93d7aeb6"  
            )
        ]

        private_subnets = [
            ec2.Subnet.from_subnet_attributes(
                self,
                "PrivateSubnetA",
                availability_zone="eu-west-1b",
                subnet_id="subnet-04b7aeaa5a76811a0"  
            ),
            ec2.Subnet.from_subnet_attributes(
                self,
                "PrivateSubnetB",
                availability_zone="eu-west-1b",
                subnet_id="subnet-033dac9b4c4e65d30"  
            )
        ]

        # Import all existing security groups
        security_group_1 = ec2.SecurityGroup.from_security_group_id(
            self,
            "SecurityGroup1",
            security_group_id="sg-0dc8f9498ea364d11"
        )

        security_group_2 = ec2.SecurityGroup.from_security_group_id(
            self,
            "SecurityGroup2",
            security_group_id="sg-06982dd85d3af4984"
        )

        security_group_3 = ec2.SecurityGroup.from_security_group_id(
            self,
            "SecurityGroup3",
            security_group_id="sg-07c3ae76cdbf0e95e"
        )

        security_group_4 = ec2.SecurityGroup.from_security_group_id(
            self,
            "SecurityGroup4",
            security_group_id="sg-0c95d97d4c25beec0"
        )

        security_group_5 = ec2.SecurityGroup.from_security_group_id(
            self,
            "SecurityGroup5",
            security_group_id="sg-05c82157d13f08fc0"
        )

        alb_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "ALBSecurityGroup",
            security_group_id="sg-03283c9d871a30e67"
        )

        rds_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "RDSSecurityGroup",
            security_group_id="sg-07c3ae76cdbf0e95e"
        )

        bastion_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "BastionSecurityGroup",
            security_group_id="sg-06982dd85d3af4984"
        )

        patient_portal_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "PatientPortalSecurityGroup",
            security_group_id="sg-027be1ac97a24df45"
        )

        # Import existing IAM role
        task_execution_role = iam.Role.from_role_arn(
            self,
            "TaskExecutionRole",
            role_arn=f"arn:aws:iam::{Stack.of(self).account}:role/PrimumAiStageStack-EcsConstructEcsTaskExecutionRole-RIm5XA6A5Jnc"
        )

        # Create ECS Cluster with capacity providers
        self.cluster = ecs.Cluster(
            self, 
            "PrimumaiAiAuthCluster",
            cluster_name="primumaiAiAuth",  
            vpc=self.vpc,
            container_insights=False,
            enable_fargate_capacity_providers=True
        )

        # Create Task Definition with the existing execution role
        task_definition = ecs.FargateTaskDefinition(
            self,
            "PrimumaAiAuthTask",
            memory_limit_mib=3072,  
            cpu=1024,  
            execution_role=task_execution_role,
            task_role=task_execution_role  
        )

        # Add container to task definition
        container = task_definition.add_container(
            "PrimumaiAuthAiContainer",  
            image=ecs.ContainerImage.from_registry("148761648660.dkr.ecr.eu-west-1.amazonaws.com/primumai_ai_auth_service"),
            memory_limit_mib=3072,
            port_mappings=[ecs.PortMapping(
                container_port=80,
                host_port=80,
                protocol=ecs.Protocol.TCP,
                name="ai-authaicontainer-80-tcp"
            )],
            environment={
                "JWT_SECRET_OTP": "otpSecret123",
                "JWT_SECRET_WELCOME": "welcomeSecret123",
                "JWT_SECRET_SESSION": "sessionSecret123",
                "DB_HOST": "localhost",
                "DB_USER": "root",
                "DB_PASS": "",
                "DB_NAME": "auth_microservice",
                "DB_PORT": "3306",
                "AWS_REGION": "eu-west-1",
                "AWS_KEYSTRING": "RdsConstructDBCredentialsSe-HuvS1juo8rDK",
                "APP_ENV": "production",
                "VALKEY_URL": "clustercfg.valkey-cache.hlr47x.memorydb.eu-west-1.amazonaws.com:6379"
            }
        )


        # Create ALB with our naming
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "PrimumaiAuthALB",
            vpc=self.vpc,
            internet_facing=True,
            security_group=security_group_1, 
            vpc_subnets=ec2.SubnetSelection(subnets=[
                ec2.Subnet.from_subnet_attributes(
                    self,
                    "ALBPublicSubnet",
                    availability_zone="eu-west-1a",
                    subnet_id="subnet-03ba29a1f6c9783c8"
                ),
                ec2.Subnet.from_subnet_attributes(
                    self,
                    "ALBPrivateSubnet",
                    availability_zone="eu-west-1b",
                    subnet_id="subnet-033dac9b4c4e65d30"
                )
            ])
        )

        # Create Target Group
        target_group = elbv2.ApplicationTargetGroup(
            self,
            "PrimumaiAuthTargetGroup1",
            vpc=self.vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            health_check=elbv2.HealthCheck(
                path="/api/health-check",
                healthy_threshold_count=2,
                unhealthy_threshold_count=10
            ),
            deregistration_delay=Duration.seconds(300)
        )

        # Add listener BEFORE creating the service
        listener = self.alb.add_listener(
            "Listener",
            port=80,
            default_target_groups=[target_group]
        )

        # Create ECS Service with our naming
        self.service = ecs.FargateService(
            self,
            "PrimumaiAuthService",
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=1,
            security_groups=[ 
                security_group_1,
                security_group_2,
                security_group_3,
                security_group_4,
                security_group_5
            ],
            vpc_subnets=ec2.SubnetSelection(subnets=[
                ec2.Subnet.from_subnet_attributes(
                    self,
                    "ServicePublicSubnetA",
                    availability_zone="eu-west-1a",
                    subnet_id="subnet-03ba29a1f6c9783c8"
                ),
                ec2.Subnet.from_subnet_attributes(
                    self,
                    "ServicePrivateSubnetB",
                    availability_zone="eu-west-1b",
                    subnet_id="subnet-033dac9b4c4e65d30"
                )
            ]),
            assign_public_ip=True,
            platform_version=ecs.FargatePlatformVersion.LATEST,
            circuit_breaker=ecs.DeploymentCircuitBreaker(
                rollback=True
            ),
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.ECS
            ),
            enable_ecs_managed_tags=True,
            health_check_grace_period=Duration.seconds(60)
        )

        # Register the service with the target group
        self.service.attach_to_application_target_group(target_group)