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

@dataclass
class Node:
    name: str
    gpus_total: int
    cpus_total: int
    memory_total: int

    gpus_available: int
    cpus_available: int
    memory_available: int

@dataclass
class Cluster:
    nodes: list[Node]
    def available_nodes(self) -> list[Node]:
        return [node for node in self.nodes if node.gpus_available > 0 or node.cpus_avalable > 0 or node.memory_available > 0]