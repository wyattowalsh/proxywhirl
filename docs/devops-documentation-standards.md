# Documentation Standards

## Runbook Template

```markdown
# [Service Name] [Issue]

## Severity
[Critical/High/Medium/Low]

## Prerequisites
- [ ] Verify service status
- [ ] Check recent deployments
- [ ] Review logs

## Investigation Steps
1. Step 1
2. Step 2
3. Step 3

## Resolution
1. Action 1
2. Action 2
3. Action 3

## Validation
```bash
# Verification commands
```

## Rollback
1. Rollback step 1
2. Rollback step 2

## Post-Incident
- [ ] Update monitoring
- [ ] Create ticket for root cause fix
- [ ] Post in #incidents slack
```

## Playbook Template

```markdown
# [Service Name] Playbook

## Overview
Brief description of service and responsibilities

## Contact & Escalation
- On-call: @service-oncall
- Manager: @team-manager
- VP: @vp-engineering

## Critical Paths
1. Customer request flows through:
   [Service A] → [Service B] → [Database]

## Key Metrics
- Latency (p99): 
- Error rate:
- Throughput:

## Common Issues
### Issue 1
- Symptom: 
- Diagnosis:
- Fix:
```

## Wiki Standards

- All runbooks in `/docs/devops-runbooks/`
- All playbooks in `/docs/devops-playbooks/`
- Markdown format with code blocks
- Review by 2 engineers before production
- Update within 1 week of incident
