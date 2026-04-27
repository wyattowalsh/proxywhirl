# ProxyWhirl Terraform Module for AWS Deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
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
      }
    ]
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
    assign_public_ip = true
  }

  tags = local.tags
}

# Auto Scaling
resource "aws_appautoscaling_target" "proxywhirl_target" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.proxywhirl.name}/${aws_ecs_service.proxywhirl.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Variables
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

variable "app_version" {
  default = "latest"
}

variable "docker_image" {
  default = "proxywhirl"
}

variable "desired_count" {
  default = 3
}

variable "min_capacity" {
  default = 2
}

variable "max_capacity" {
  default = 10
}

variable "subnet_ids" {
  type = list(string)
}

# Tags
locals {
  tags = {
    Environment = var.environment
    Project     = "proxywhirl"
    Terraform   = "true"
  }
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
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}
