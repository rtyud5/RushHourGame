import time
import psutil
import os
from typing import Dict, Any, Optional


class Statistics: 
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.algorithm_name = ""
        self.start_time = 0.0
        self.end_time = 0.0
        self.search_time = 0.0
        self.expanded_nodes = 0
        self.memory_usage = 0.0  # in MB
        self.initial_memory = 0.0
        self.solution_length = 0
        self.solution_found = False
        self.solution_path = []
        
    def start_tracking(self, algorithm_name: str):
        self.reset()
        self.algorithm_name = algorithm_name
        self.start_time = time.time()
        self.initial_memory = self._get_memory_usage()
        
    def stop_tracking(self):
        self.end_time = time.time()
        self.search_time = self.end_time - self.start_time
        # Ensure memory usage is never negative
        memory_diff = self._get_memory_usage() - self.initial_memory
        self.memory_usage = max(0.0, memory_diff)
        
    def increment_expanded_nodes(self): 
        self.expanded_nodes += 1
        
    def set_solution(self, path: list):
        self.solution_found = True
        self.solution_path = path
        self.solution_length = len(path)
        
    def _get_memory_usage(self) -> float:
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert bytes to MB
        except:
            return 0.0
            
    def get_summary(self) -> Dict[str, Any]:
        return {
            'algorithm': self.algorithm_name,
            'search_time': self.search_time,
            'memory_usage': self.memory_usage,
            'expanded_nodes': self.expanded_nodes,
            'solution_found': self.solution_found,
            'solution_length': self.solution_length,
        }
        
    def format_time(self, seconds: float) -> str:
        if seconds < 0.001:
            return f"{seconds * 1_000_000:.0f}µs"
        elif seconds < 1.0:
            return f"{seconds * 1000:.2f}ms"
        else:
            return f"{seconds:.3f}s"
            
    def format_memory(self, mb: float) -> str:
        # Ensure memory value is not negative
        mb = max(0.0, mb)
        if mb < 1.0:
            return f"{mb * 1024:.1f}KB"
        else:
            return f"{mb:.2f}MB"
            
    def get_formatted_stats(self) -> Dict[str, str]:
        return {
            'algorithm': self.algorithm_name,
            'time': self.format_time(self.search_time),
            'memory': self.format_memory(self.memory_usage),
            'expanded_nodes': str(self.expanded_nodes),
            'solution_length': str(self.solution_length),
            'status': 'Solved' if self.solution_found else 'No Solution'
        } 
