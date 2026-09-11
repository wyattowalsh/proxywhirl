# NOTE: This directory is a partial ECS scaffold. Outputs below match resources defined in main.tf only.
# Planned modules (ALB, RDS, ElastiCache, monitoring) referenced in older revisions are not implemented.

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.proxywhirl.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.proxywhirl.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for ECS tasks"
  value       = aws_cloudwatch_log_group.proxywhirl.name
}

output "security_group_id" {
  description = "Security group attached to the ECS service"
  value       = aws_security_group.proxywhirl.id
}

output "assign_public_ip" {
  description = "Whether Fargate tasks receive public IPs (default false)"
  value       = var.assign_public_ip
}

output "secrets_backend_arn" {
  description = "Secrets Manager or SSM ARN used for task secret injection"
  value       = local.secrets_arn
  sensitive   = true
}