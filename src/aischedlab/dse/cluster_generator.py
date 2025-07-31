from aischedlab.core.models import Cluster, Node
import random

class ClusterGenerator:
    def __init__(self, nodes: list[Node]):
        """
        Initialize the ClusterGenerator with the number of nodes and their capacity.

        :param nodes: List of Node objects in the cluster.
        """
        self.nodes = nodes

    def generate_nodes(self, gpu_range: tuple[int, int], cpu_range: tuple[int, int], memory_range: tuple[int, int], node_ram_range: tuple[int, int]) -> list[Node]:
        """
        Generate a list of Node objects with the specified configuration.
        
        :return: A list of Node objects.
        """
        nodes = []

        for i in range(len(self.nodes)):
            node = self.nodes[i]
            node.gpu = random.randint(*gpu_range)
            node.cpu = random.randint(*cpu_range)
            node.memory = random.randint(*memory_range)
            node.ram = random.randint(*node_ram_range)
            nodes.append(node)
        
        return nodes

    def generate(self) -> Cluster:
        """
        Generate a Cluster object with the specified number of nodes and their capacity.
        
        :return: A Cluster object with the defined configuration.
        """
        return Cluster(nodes=self.nodes)
        