from aischedlab.core.models import Job, Cluster
import simpy
import logging

from aischedlab.core.base_scheduler import BaseScheduler
from aischedlab.core.metric_collector import MetricCollector  # Ensure correct import

logger = logging.getLogger(__name__)

class BackfillScheduler(BaseScheduler):
    def __init__(self, cluster: Cluster):
        super().__init__(cluster)
    
    def schedule(self, env: simpy.Environment, job: Job, metrics: MetricCollector):
        yield env.timeout(job.submit_time - env.now)
        logger.info(f"[{env.now}] Job {job.name} submitted")
        metrics.record_job_submission(job, env)

        self.jobs.append(job)

        while True:
            if not self.jobs:
                logger.info(f"[{env.now}] No jobs to schedule, exiting scheduler for job {job.name}.")
                break  # Exit the loop and end this process

            # Sort jobs by their submit time
            self.jobs.sort(key=lambda j: j.submit_time)
            primary_job = self.jobs[0]
            earliest_start = self._find_earliest_start(env, primary_job)

            for job in self.jobs:
                if self._can_backfill(job, earliest_start):
                    if job in self.jobs:
                        self.jobs.remove(job)
                    logger.info(f"[{env.now}] Job {job.name} backfilled")
                    env.process(self._run_job(env, job, metrics))
                    break
                else:
                    logger.info(f"[{env.now}] No job can be backfilled, waiting...")
                    if self._can_schedule(primary_job):
                        if primary_job in self.jobs:
                            self.jobs.remove(primary_job)
                        env.process(self._run_job(env, primary_job, metrics))
                    else:
                        yield env.timeout(1)
    
    def _run_job(self, env, job: Job, metrics: MetricCollector):
        node = self._find_available_node(job)
        if not node:
            logger.warning(f"[{env.now}] No available node for job {job.name}")
            return

        # Set waiting time and record job start
        job.waiting_time = env.now - job.submit_time
        metrics.record_job_start(job, env)
        metrics.record_utilization(env, self.cluster)

        node.gpus_available -= job.gpus
        node.cpus_available -= job.cpus
        node.memory_available -= job.memory
        logger.info(f"[{env.now}] Job {job.name} scheduled on node {node.name}")
        yield env.timeout(job.duration)
        logger.info(f"[{env.now}] Job {job.name} completed on node {node.name}")

        node.gpus_available += job.gpus
        node.cpus_available += job.cpus
        node.memory_available += job.memory

        metrics.record_job_end(job, env)
        metrics.record_utilization(env, self.cluster)
        metrics.record_energy(node)

    def _can_schedule(self, job: Job) -> bool:
        return any(node.gpus_available >= job.gpus and
                   node.cpus_available >= job.cpus and
                   node.memory_available >= job.memory for node in self.cluster.nodes)
    
    def _find_available_node(self, job: Job):
        for node in self.cluster.nodes:
            if (node.gpus_available >= job.gpus and
                node.cpus_available >= job.cpus and
                node.memory_available >= job.memory):
                logger.info(f"Found available node {node.name} for job {job.name}")
                return node
        return None
    
    def _find_earliest_start(self, env, job: Job) -> int:
        logger.info(f"Finding earliest start time for job {job.name}")
        return env.now + min((j.submit_time for j in self.jobs if j != job), default=env.now)
    
    def _can_backfill(self, job: Job, earliest_start: int):
        logger.info(f"Checking if job {job.name} can be backfilled at time {earliest_start}")
        return earliest_start < job.submit_time and self._can_schedule(job)