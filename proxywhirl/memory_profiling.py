"""Memory profiling utilities."""

import tracemalloc
from typing import Optional, Dict, List
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    total_mb: float
    peak_mb: float
    current_mb: float
    allocations: int


class MemoryProfiler:
    """Profiles memory usage."""
    
    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        tracemalloc.start()
    
    @contextmanager
    def profile_block(self, name: str):
        """Profile a code block."""
        tracemalloc.reset_peak()
        snapshot_before = tracemalloc.take_snapshot()
        
        try:
            yield
        finally:
            snapshot_after = tracemalloc.take_snapshot()
            current, peak = tracemalloc.get_traced_memory()
            
            stats = snapshot_after.compare_to(snapshot_before, 'lineno')
            
            self.snapshots.append(MemorySnapshot(
                total_mb=current / 1024 / 1024,
                peak_mb=peak / 1024 / 1024,
                current_mb=current / 1024 / 1024,
                allocations=len(stats)
            ))
    
    def get_top_allocations(self, limit: int = 10) -> List[str]:
        """Get top memory allocations."""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        results = []
        for stat in top_stats[:limit]:
            results.append(f"{stat.filename}:{stat.lineno} {stat.size / 1024}KB")
        return results
    
    def get_summary(self) -> Dict:
        """Get memory profiling summary."""
        current, peak = tracemalloc.get_traced_memory()
        return {
            "current_mb": current / 1024 / 1024,
            "peak_mb": peak / 1024 / 1024,
            "snapshots_count": len(self.snapshots)
        }

