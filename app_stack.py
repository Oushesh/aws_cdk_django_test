import aws_cdk
from aws_cdk import (
    core,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2
)


class AppStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository for storing the Docker images
        self.repository = ecr.Repository(
            self, "MyDjangoApp", repository_name="my-django-app"
        )

        # Create an ECS cluster
        self.cluster = ecs.Cluster(
            self, "MyCluster", vpc=ecs.VpcConfig()
        )

        # Create a task definition for running the Django app
        self.task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            cpu=1024, memory_limit_mib=2048
        )

        # Add a container to the task definition
        django_container = self.task_definition.add_container(
            "DjangoApp",
            image=ecr.ContainerImage.from_repository(self.repository),
            environment={
                "DJANGO_SETTINGS_MODULE": "myapp.settings"
            },
            command=["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
        )

        # Define port mapping for the container
        django_container.add_port_mappings(
            ecs.PortMapping(container_port=8000)
        )

        # Create a service to run the task definition
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Service",
            cluster=self.cluster,
            task_definition=self.task_definition,
            desired_count=1,
            public_load_balancer=True
        )

