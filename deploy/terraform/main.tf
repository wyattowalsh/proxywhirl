terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "proxywhirl-terraform"
    key            = "proxywhirl/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "proxywhirl-tf-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "proxywhirl"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

module "vpc" {
  source = "./modules/vpc"
  
  environment    = var.environment
  cidr_block     = var.vpc_cidr
  azs            = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
}

module "ecs" {
  source = "./modules/ecs"
  
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  container_image     = var.container_image
  container_port      = var.container_port
  desired_count       = var.ecs_desired_count
  min_count           = var.ecs_min_count
  max_count           = var.ecs_max_count
  cpu_target_value    = var.ecs_cpu_target
  memory_target_value = var.ecs_memory_target
}

module "rds" {
  source = "./modules/rds"
  
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  instance_class  = var.rds_instance_class
  allocated_storage = var.rds_allocated_storage
  db_name         = var.rds_db_name
  username        = var.rds_username
}

module "elasticache" {
  source = "./modules/elasticache"
  
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  node_type       = var.redis_node_type
  num_cache_nodes = var.redis_num_nodes
}

module "alb" {
  source = "./modules/alb"
  
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  target_group_arn  = module.ecs.target_group_arn
  certificate_arn   = var.acm_certificate_arn
}

module "monitoring" {
  source = "./modules/monitoring"
  
  environment          = var.environment
  ecs_cluster_name     = module.ecs.cluster_name
  ecs_service_name     = module.ecs.service_name
  rds_db_instance_id   = module.rds.db_instance_id
  elasticache_cluster_id = module.elasticache.cluster_id
  sns_topic_arn        = aws_sns_topic.alerts.arn
}

resource "aws_sns_topic" "alerts" {
  name = "proxywhirl-${var.environment}-alerts"
}

resource "aws_sns_topic_subscription" "alert_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.db_endpoint
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.elasticache.endpoint
}
