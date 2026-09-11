# ProxyWhirl Terraform Module for AWS Deployment
#
# Hardening defaults:
# - assign_public_ip = false (private subnets + NAT / ALB ingress)
# - app_version must be an explicit semver/tag (not "latest")
# - API/cache secrets injected from AWS Secrets Manager or SSM Parameter Store ARNs

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = {
    Environment = var.environment
    Project     = "proxywhirl"
    Terraform   = "true"
  }

  # Prefer Secrets Manager; fall back to SSM Parameter Store ARN pattern.
  secrets_arn = (
    var.secrets_manager_secret_arn != "" ? var.secrets_manager_secret_arn :
    var.ssm_parameter_arn != "" ? var.ssm_parameter_arn :
    null
  )
}

check "secrets_backend_configured" {
  assert {
    condition     = local.secrets_arn != null
    error_message = "Set secrets_manager_secret_arn or ssm_parameter_arn for API/cache secrets."
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "proxywhirl" {
  name = "proxywhirl-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.tags
}

# ECS Task Definition
resource "aws_ecs_task_definition" "proxywhirl" {
  family                   = "proxywhirl"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([{
    name      = "proxywhirl"
    image     = "${var.docker_image}:${var.app_version}"
    essential = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]
    environment = [
      {
        name  = "ENVIRONMENT"
        value = var.environment
      },
      {
        name  = "PROXYWHIRL_REQUIRE_AUTH"
        value = "true"
      },
      {
        name  = "PROXYWHIRL_PUBLIC_METRICS"
        value = "false"
      },
      {
        name  = "PROXYWHIRL_BIND_HOST"
        value = "0.0.0.0"
      }
    ]
    secrets = [
      {
        name      = "PROXYWHIRL_API_KEY"
        valueFrom = "${local.secrets_arn}:api-key::"
      },
      {
        name      = "PROXYWHIRL_CACHE_ENCRYPTION_KEY"
        valueFrom = "${local.secrets_arn}:cache-encryption-key::"
      }
    ]
    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5)\""]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 10
    }
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.proxywhirl.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
  }])

  tags = local.tags
}

# ECS Service
resource "aws_ecs_service" "proxywhirl" {
  name            = "proxywhirl"
  cluster         = aws_ecs_cluster.proxywhirl.id
  task_definition = aws_ecs_task_definition.proxywhirl.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.proxywhirl.id]
    assign_public_ip = var.assign_public_ip
  }

  tags = local.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "proxywhirl" {
  name              = "/ecs/proxywhirl"
  retention_in_days = 7

  tags = local.tags
}

# Security Group
resource "aws_security_group" "proxywhirl" {
  name = "proxywhirl-${var.environment}"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.allowed_ingress_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}
