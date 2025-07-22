from core.models import Job, Cluster
import simpy
import logging
from core.base_scheduler import BaseScheduler

logger = logging.getLogger(__name__)

class FIFOScheduler(BaseScheduler):
    def __init__(self, cluster: Cluster):
        super().__init__(cluster)

    def schedule(self, env: simpy.Environment, job: Job):
        yield env.timeout(job.submit_time - env.now)
        logger.info(f"[{env.now}] Job {job.name} submitted")

        while True:
            for node in self.cluster.nodes:
                if (node.gpus_available >= job.gpus and
                    node.cpus_available >= job.cpus and
                    node.memory_available >= job.memory):

                    # Record waiting time
                    job.waiting_time = env.now - job.submit_time

                    node.gpus_available -= job.gpus
                    node.cpus_available -= job.cpus 
                    node.memory_available -= job.memory
                    logger.info(f"[{env.now}] Job {job.name} scheduled on node {node.name}")

                    yield env.timeout(job.duration)

                    node.gpus_available += job.gpus
                    node.cpus_available += job.cpus
                    node.memory_available += job.memory
                    logger.info(f"[{env.now}] Job {job.name} completed on node {node.name}")
                    return
            yield env.timeout(1)  # Wait for 1 time unit before checking again
