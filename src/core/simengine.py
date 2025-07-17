import simpy
from core.models import Job, Cluster
from core.strategies.fifo import FIFOScheduler
import logging

logger = logging.getLogger(__name__)

class SimulationEngine:
    def __init__(self, cluster: Cluster, jobs: list[Job], scheduler_cls=FIFOScheduler):
        self.cluster = cluster
        self.jobs = sorted(jobs, key=lambda j: j.submit_time)
        self.scheduler_cls = scheduler_cls

    def run(self):
        env = simpy.Environment()
        scheduler = self.scheduler_cls(self.cluster)

        for job in self.jobs:
            env.process(scheduler.schedule(env, job))
        
        logger.info("Starting simulation...")
        # Run the simulation until all jobs are processed
        env.run()
        logger.info("Simulation completed.")
