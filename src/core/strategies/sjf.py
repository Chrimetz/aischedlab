from core.models import Job, Cluster
import simpy
import logging

logger = logging.getLogger(__name__)

class SJFJobScheduler:
    def __init__(self, cluster: Cluster):
        self.cluster = cluster
        self.jobs = []

    def schedule(self, env: simpy.Environment, job: Job):
        yield env.timeout(job.submit_time - env.now)
        logger.info(f"[{env.now}] Job {job.name} submitted")

        self.jobs.append(job)
        
        while True:
            self.jobs.sort(key=lambda j: j.duration)  # Sort jobs by duration (SJF)
            for job in self.jobs:
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
                        
                        if job in self.jobs:
                            self.jobs.remove(job)
                            logger.info(f"[{env.now}] Job {job.name} removed from queue")
                        return
            yield env.timeout(1)

