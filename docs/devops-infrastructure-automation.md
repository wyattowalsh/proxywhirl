# Infrastructure Automation (IaC)

## Terraform Modules

All infrastructure defined as code in `deploy/terraform/`:

```
deploy/terraform/
├── main.tf                    # Core ECS/ALB setup
├── variables.tf               # Configurable values
├── vpc.tf                     # Network configuration
├── rds.tf                     # Database setup
├── elasticache.tf             # Redis cluster
├── monitoring.tf              # CloudWatch/SNS
└── environments/
    ├── staging.tfvars
    └── production.tfvars
```

## Ansible Playbooks

Configuration management in `deploy/ansible/`:

```yaml
# site.yml - Main playbook
- hosts: all
  roles:
    - common          # Base packages, security
    - docker          # Docker runtime
    - proxywhirl      # App deployment
    - monitoring      # Agent installation
```

## GitOps Workflow

All changes go through:
1. Create branch with changes
2. Plan: `terraform plan -var-file=staging.tfvars`
3. Review in pull request
4. Merge to main
5. Apply: `terraform apply -auto-approve`

## Infrastructure Testing

```bash
# Terraform validation
terraform validate
terraform fmt -check

# Policy as code
tfsec deploy/terraform/
checkov -d deploy/terraform/

# Plan diff
terraform plan -json | jq .resource_changes
```

## Disaster Recovery Testing

```bash
# Monthly DR drill
- Teardown staging environment
- Rebuild from IaC
- Run smoke tests
- Verify within RTO (1 hour)
```
