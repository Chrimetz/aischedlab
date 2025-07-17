import yaml
from core.models import Cluster, Job, Node
import logging

logger = logging.getLogger(__name__)

def load_jobs(path: str) -> list[Job]:
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return [Job(**item) for item in data]

def load_cluster(path: str) -> Cluster:
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    nodes = [Node(**item) for item in data['nodes']]
    return Cluster(nodes=nodes)