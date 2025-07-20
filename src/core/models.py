from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    name: str
    submit_time: int
    duration: int
    gpus: int
    cpus: int = 1
    memory: int = 0 # in GB
    waiting_time: int = 0

@dataclass
class Node:
    name: str
    gpus_total: int
    cpus_total: int
    memory_total: int

    gpus_available: int
    cpus_available: int
    memory_available: int

    power_idle: float = 100.0 # Watts in idle state
    power_active: float = 300.0 # Watts in active state
    energy_consumption: float = 0.0 # kWh

    def utilization(self) -> float:
        used_gpus = self.gpus_total - self.gpus_available
        return (used_gpus / self.gpus_total) * 100 if self.gpus_total > 0 else 0

@dataclass
class Cluster:
    nodes: list[Node]
    def available_nodes(self) -> list[Node]:
        return [node for node in self.nodes if node.gpus_available > 0 or node.cpus_avalable > 0 or node.memory_available > 0]