import re
import yaml
from aischedlab.core.models import Cluster, Job, Node
import logging

logger = logging.getLogger(__name__)

def expand_nodes(node_def):
    # Expand pattern if present
    if "name_pattern" in node_def:
        pattern = node_def["name_pattern"]
        match = re.search(r"\[(\d+)-(\d+)\]", pattern)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            nodes = []
            for i in range(start, end + 1):
                node = node_def.copy()
                node["name"] = pattern.replace(match.group(0), str(i))
                node.pop("name_pattern", None)
                node.pop("count", None)
                nodes.append(node)
            return nodes
        else:
            # If pattern is present but not matched, remove it
            node = node_def.copy()
            node.pop("name_pattern", None)
            node.pop("count", None)
            return [node]
    # Remove count if present
    node = node_def.copy()
    node.pop("count", None)
    return [node]

def load_jobs(path: str) -> list[Job]:
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return [Job(**item) for item in data]

def load_cluster(path: str) -> Cluster:
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    nodes = []
    for node_def in data["nodes"]:
        nodes.extend(expand_nodes(node_def))
    # Create Node objects
    node_objs = [Node(**node) for node in nodes]
    # Create and return Cluster object
    return Cluster(nodes=node_objs)