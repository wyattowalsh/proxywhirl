# Variables for the partial ECS scaffold in main.tf.
# Planned ALB/RDS/ElastiCache inputs from older revisions are not wired yet.

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, production, prod."
  }
}

variable "app_version" {
  description = "Container image tag (semver or commit SHA). Must not be 'latest'."
  type        = string

  validation {
    condition     = var.app_version != "latest" && var.app_version != ""
    error_message = "app_version must be an explicit pin (semver/SHA), not 'latest'."
  }
}

variable "docker_image" {
  description = "Container image repository (without tag)"
  type        = string
  default     = "ghcr.io/wyattowalsh/proxywhirl"
}

variable "desired_count" {
  description = "Desired ECS task count; SQLite deployments support one writer"
  type        = number
  default     = 1

  validation {
    condition     = var.desired_count == 1
    error_message = "desired_count must remain 1 until shared/external storage is implemented."
  }
}

variable "subnet_ids" {
  description = "Subnet IDs for the Fargate service (prefer private)"
  type        = list(string)
}

variable "allowed_ingress_cidr_blocks" {
  description = "CIDR blocks allowed to reach the API port (avoid 0.0.0.0/0 in production)"
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Assign public IPs to Fargate tasks. Default false — use private subnets + NAT/ALB."
  type        = bool
  default     = false
}

variable "secrets_manager_secret_arn" {
  description = "ARN of Secrets Manager secret JSON with keys: api-key and cache-encryption-key"
  type        = string
  default     = ""
}

variable "ssm_parameter_arn" {
  description = "Fallback SSM Parameter Store ARN for the same secret JSON when Secrets Manager is unused"
  type        = string
  default     = ""
}

variable "ecs_execution_role_arn" {
  description = "IAM role ARN for ECS task execution (must allow secretsmanager:GetSecretValue / ssm:GetParameters)"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "IAM role ARN for the running task"
  type        = string
  default     = null
}
