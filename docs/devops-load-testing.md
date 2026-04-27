# Load Testing & Capacity Planning

## Load Testing Tools

### Apache JMeter
```jmx
<ThreadGroup guiclass="ThreadGroupGui" testname="Load Test">
  <elementProp name="ThreadGroup.main_controller">
    <stringProp name="ThreadGroup.num_threads">100</stringProp>
    <stringProp name="ThreadGroup.ramp_time">60</stringProp>
    <stringProp name="ThreadGroup.duration">300</stringProp>
  </elementProp>
</ThreadGroup>
```

### Locust
```python
from locust import HttpUser, task

class ProxyWhirlUser(HttpUser):
    @task
    def get_proxies(self):
        self.client.get("/api/v1/proxies")
    
    @task
    def select_proxy(self):
        self.client.post("/api/v1/select")
```

### k6
```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function() {
  const res = http.get('http://api.proxywhirl.local/proxies');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```

## Capacity Planning

Target metrics:
- Throughput: 10k req/s
- Latency (p99): < 500ms
- Error rate: < 0.1%
- Connection pool: 200 concurrent

Estimated requirements:
- API servers: 5 instances (2 vCPU, 4 GB RAM each)
- Database: 1 primary + 2 replicas (16 vCPU, 64 GB RAM)
- Cache: 3-node Redis cluster (4 GB each)
