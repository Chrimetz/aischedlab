import simpy
from aischedlab.core.models import Job, Cluster
from aischedlab.core.strategies.fifo import FIFOScheduler
import logging
import numpy as np
from aischedlab.core.metric_collector import MetricCollector

logger = logging.getLogger(__name__)

class SimulationEngine:
    def __init__(self, cluster: Cluster, jobs: list[Job], scheduler_cls=FIFOScheduler):
        self.cluster = cluster
        self.jobs = sorted(jobs, key=lambda j: j.submit_time)
        self.scheduler_cls = scheduler_cls
        self.metrics = MetricCollector()

    def run(self):
        env = simpy.Environment()
        scheduler = self.scheduler_cls(self.cluster)
        done_event = env.event()  # Event to signal all jobs are done

        # Start energy tracking process
        env.process(self.track_energy(env, self.cluster, done_event))

        # Start all job processes and collect their events
        job_events = []
        for job in self.jobs:
            job_event = env.event()
            env.process(self._job_wrapper(scheduler, env, job, job_event, self.metrics))
            job_events.append(job_event)

        logger.info("Starting simulation...")

        # When all job_events are triggered, succeed the done_event
        def all_jobs_done(env, job_events, done_event):
            yield simpy.events.AllOf(env, job_events)
            done_event.succeed()
        env.process(all_jobs_done(env, job_events, done_event))

        env.run()
        logger.info("Simulation completed.")
        self.metrics.report(output_file=f"metrics_scheduler_{self.scheduler_cls.__name__}.csv")

    @staticmethod
    def track_energy(env, cluster: Cluster, done_event, interval=1):
        while not done_event.triggered:
            for node in cluster.nodes:
                node.energy_consumption += node.power_active * interval / 3600  # Convert Watts to kWh
            yield env.timeout(interval)

    @staticmethod
    def _job_wrapper(scheduler, env, job, job_event, metrics: MetricCollector):
        yield from scheduler.schedule(env, job, metrics)
        job_event.succeed()

    def print_summary(self):
        logger.info("Simulation Summary:")
        for node in self.cluster.nodes:
            logger.info(f"Node {node.name}:")
            logger.info(f"  Total GPUs: {node.gpus_total}")
            logger.info(f"  Total CPUs: {node.cpus_total}")
            logger.info(f"  Total Memory: {node.memory_total} GB")
            logger.info(f"  Energy Consumption: {node.energy_consumption:.2f} kWh")
        total_energy = sum(node.energy_consumption for node in self.cluster.nodes)
        logger.info(f"Total Energy Consumption: {total_energy:.2f} kWh")

        # --- Waiting time metrics ---
        waiting_times = [getattr(job, "waiting_time", 0) for job in self.jobs]
        if waiting_times:
            avg_wait = np.mean(waiting_times)
            q25 = np.quantile(waiting_times, 0.25)
            q50 = np.quantile(waiting_times, 0.5)
            q75 = np.quantile(waiting_times, 0.75)
            logger.info("Job Waiting Time Statistics:")
            for job in self.jobs:
                logger.info(f"  Job {job.name}: Waiting Time = {getattr(job, 'waiting_time', 0)}")
            logger.info(f"  Average Waiting Time: {avg_wait:.2f}")
            logger.info(f"  25th Percentile: {q25:.2f}")
            logger.info(f"  Median: {q50:.2f}")
            logger.info(f"  75th Percentile: {q75:.2f}")