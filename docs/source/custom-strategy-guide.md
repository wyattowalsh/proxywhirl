# Creating Custom Rotation Strategies

## Strategy Interface

All strategies must implement the RotationStrategy protocol:

```python
from typing import List
from proxywhirl import Proxy, RotationStrategy

class CustomStrategy(RotationStrategy):
    def select(self, proxies: List[Proxy]) -> Proxy:
        """Select a proxy from the list"""
        pass
    
    def get_weight(self, proxy: Proxy) -> float:
        """Get weight for scoring"""
        pass
    
    def on_success(self, proxy: Proxy) -> None:
        """Called when proxy succeeds"""
        pass
    
    def on_failure(self, proxy: Proxy) -> None:
        """Called when proxy fails"""
        pass
```

## Simple Custom Strategy

### Example: Least Used Strategy

```python
from proxywhirl import RotationStrategy

class LeastUsedStrategy(RotationStrategy):
    def __init__(self):
        self.usage_count = {}
    
    def select(self, proxies: List[Proxy]) -> Proxy:
        # Select proxy with least usage
        selected = min(proxies, 
            key=lambda p: self.usage_count.get(p.url, 0))
        self.usage_count[selected.url] = \
            self.usage_count.get(selected.url, 0) + 1
        return selected
    
    def get_weight(self, proxy: Proxy) -> float:
        return 1.0 / (self.usage_count.get(proxy.url, 1) + 1)
    
    def on_success(self, proxy: Proxy) -> None:
        pass  # Success is already counted
    
    def on_failure(self, proxy: Proxy) -> None:
        # Reset failed proxy
        self.usage_count[proxy.url] = 0
```

## Advanced Custom Strategy

### Example: Performance-Based with Learning

```python
from datetime import datetime, timedelta
from proxywhirl import RotationStrategy

class LearningStrategy(RotationStrategy):
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.performance = {}  # url -> [latencies]
        self.success_rate = {}  # url -> success_count
    
    def select(self, proxies: List[Proxy]) -> Proxy:
        # Select based on learned performance
        scores = {}
        for proxy in proxies:
            perf = self.performance.get(proxy.url, [])
            if not perf:
                scores[proxy.url] = 0.5  # Unknown proxies get medium score
            else:
                avg_latency = sum(perf) / len(perf)
                score = 1.0 / (1.0 + avg_latency)
                scores[proxy.url] = score
        
        selected_url = max(scores, key=scores.get)
        return next(p for p in proxies if p.url == selected_url)
    
    def get_weight(self, proxy: Proxy) -> float:
        perf = self.performance.get(proxy.url, [])
        if not perf:
            return 0.5
        avg_latency = sum(perf) / len(perf)
        return 1.0 / (1.0 + avg_latency)
    
    def on_success(self, proxy: Proxy) -> None:
        if proxy.url not in self.performance:
            self.performance[proxy.url] = []
        
        # Add success latency (assume 100ms)
        self.performance[proxy.url].append(100)
        
        # Keep window size
        if len(self.performance[proxy.url]) > self.window_size:
            self.performance[proxy.url].pop(0)
        
        # Update success rate
        self.success_rate[proxy.url] = \
            self.success_rate.get(proxy.url, 0) + 1
    
    def on_failure(self, proxy: Proxy) -> None:
        if proxy.url not in self.performance:
            self.performance[proxy.url] = []
        
        # Add failure latency (assume 10000ms)
        self.performance[proxy.url].append(10000)
        
        # Keep window size
        if len(self.performance[proxy.url]) > self.window_size:
            self.performance[proxy.url].pop(0)
```

## Registering Custom Strategy

### Option 1: Direct Usage

```python
from proxywhirl import ProxyWhirl, ProxyConfiguration

config = ProxyConfiguration(
    sources=['http://example.com/proxies'],
    strategy=CustomStrategy()
)

rotator = ProxyWhirl(config=config)
```

### Option 2: Register with Factory

```python
from proxywhirl import StrategyRegistry

registry = StrategyRegistry()
registry.register('custom', CustomStrategy)

config = ProxyConfiguration(
    sources=['http://example.com/proxies'],
    strategy_config={'name': 'custom'}
)

rotator = ProxyWhirl(config=config)
```

## Testing Custom Strategy

```python
from proxywhirl import Proxy, HealthStatus

def test_custom_strategy():
    strategy = CustomStrategy()
    
    # Create test proxies
    proxies = [
        Proxy(url='http://p1:8080', protocol='http'),
        Proxy(url='http://p2:8080', protocol='http'),
        Proxy(url='http://p3:8080', protocol='http'),
    ]
    
    # Test selection
    selected = strategy.select(proxies)
    assert selected in proxies
    
    # Test callbacks
    strategy.on_success(selected)
    strategy.on_failure(selected)
    
    # Test weight
    weight = strategy.get_weight(selected)
    assert 0 <= weight <= 1
```

## Built-in Strategies

For reference, ProxyWhirl includes:
- RoundRobinStrategy
- WeightedRoundRobinStrategy
- PerformanceBasedStrategy
- GeoTargetedStrategy
- LeastConnectionsStrategy
- RandomStrategy
- ConsistentHashingStrategy
- AntiPatternStrategy
- ResilientStrategy

