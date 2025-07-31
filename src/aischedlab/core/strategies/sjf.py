from core.models import Job, Cluster
import simpy
import logging
from aischedlab.core.base_scheduler import BaseScheduler
from aischedlab.core.metric_collector import MetricCollector  # Ensure correct import

logger = logging.getLogger(__name__)

class SJFJobScheduler(BaseScheduler):
    def __init__(self, cluster: Cluster):
        super().__init__(cluster)

    def schedule(self, env: simpy.Environment, job: Job, metrics: MetricCollector):
        yield env.timeout(job.submit_time - env.now)
        logger.info(f"[{env.now}] Job {job.name} submitted")
        metrics.record_job_submission(job, env)

        self.jobs.append(job)
        
        while True:
            self.jobs.sort(key=lambda j: j.duration)  # Sort jobs by duration (SJF)
            for job in self.jobs:
                for node in self.cluster.nodes:
                    if (node.gpus_available >= job.gpus and
                        node.cpus_available >= job.cpus and
                        node.memory_available >= job.memory):

                        # Record job start and waiting time
                        job.waiting_time = env.now - job.submit_time
                        metrics.record_job_start(job, env)
                        metrics.record_utilization(env, self.cluster)

                        node.gpus_available -= job.gpus
                        node.cpus_available -= job.cpus 
                        node.memory_available -= job.memory
                        logger.info(f"[{env.now}] Job {job.name} scheduled on node {node.name}")

                        yield env.timeout(job.duration)

                        node.gpus_available += job.gpus
                        node.cpus_available += job.cpus
                        node.memory_available += job.memory
                        logger.info(f"[{env.now}] Job {job.name} completed on node {node.name}")

                        metrics.record_job_end(job, env)
                        metrics.record_utilization(env, self.cluster)
                        metrics.record_energy(node)

                        if job in self.jobs:
                            self.jobs.remove(job)
                            logger.info(f"[{env.now}] Job {job.name} removed from queue")
                        return
            yield env.timeout(1)
            metrics.record_utilization(env, self.cluster)

