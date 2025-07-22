from abc import ABC, abstractmethod
import simpy
from core.models import Job, Cluster

class BaseScheduler(ABC):
    def __init__(self, cluster: Cluster):
        """
        Initialize the base scheduler with a cluster.
        
        :param cluster: The cluster where jobs will be scheduled.
        """
        self.cluster = cluster
        self.jobs = []
    
    @abstractmethod
    def schedule(self, env: simpy.Environment, job: Job):
        """
        Schedule a job in the simulation environment.
        
        :param env: The simulation environment.
        :param job: The job to be scheduled.
        """
        pass
        