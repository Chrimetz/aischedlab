from abc import ABC, abstractmethod
import simpy
from aischedlab.core.models import Job, Cluster
from aischedlab.core.metric_collector import MetricCollector

class BaseScheduler(ABC):
    def __init__(self, cluster: Cluster):
        """
        Initialize the base scheduler with a cluster.
        
        :param cluster: The cluster where jobs will be scheduled.
        """
        self.cluster = cluster
        self.jobs = []
    
    @abstractmethod
    def schedule(self, env: simpy.Environment, job: Job, metrics: MetricCollector):
        """
        Schedule a job in the simulation environment.
        
        :param env: The simulation environment.
        :param job: The job to be scheduled.
        """
        pass
