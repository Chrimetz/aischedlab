import logging
import csv
import os

import simpy

from aischedlab.core.models import Job, Node, Cluster

logger = logging.getLogger(__name__)

class MetricCollector:
    def __init__(self):
        self.waiting_times = []
        self.job_events = []
        self.energy_usage = []
        self.utilization_samples = []

    def get_job_metrics(self):
        jobs = set(wait['job'] for wait in self.waiting_times)
        jobs.update(event['job'] for event in self.job_events)
        metrics = []
        for job in jobs:
            metrics.append({
                "job_name": job,
                "waiting_time_seconds": next((w['waiting_time'] for w in self.waiting_times if w['job'] == job), ''),
                "submit_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'submitted'), ''),
                "start_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'started'), ''),
                "end_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'ended'), ''),
            })
        return metrics

    def get_node_metrics(self):
        nodes = set(usage['node'] for usage in self.energy_usage)
        node_metrics = []
        # Extend utilization and idle time logic as needed
        for node in nodes:
            energy = sum(usage['energy'] for usage in self.energy_usage if usage['node'] == node)
            avg_util = 0  # Extend your utilization tracking for per-node stats
            avg_idle = 0  # Extend your tracking for per-node idle time
            node_metrics.append({
                "node_name": node,
                "energy_consumed_kWh": energy,
                "avg_utilization_percent": avg_util,
                "avg_idle_time_seconds": avg_idle
            })
        return node_metrics

    def get_cluster_metrics(self):
        avg_util = sum(u['utilization_percent'] for u in self.utilization_samples) / len(self.utilization_samples) if self.utilization_samples else 0
        peak_util = max((u['utilization_percent'] for u in self.utilization_samples), default=0)
        min_util = min((u['utilization_percent'] for u in self.utilization_samples), default=0)
        return {
            "avg_cluster_utilization_percent": avg_util,
            "peak_cluster_utilization_percent": peak_util,
            "min_cluster_utilization_percent": min_util
        }

    def record_job_start(self, job: Job, env: simpy.Environment):
        job.waiting_time = env.now - job.submit_time
        self.waiting_times.append({'job': job.name, 'waiting_time': job.waiting_time})
        self.job_events.append({'job': job.name, 'event': 'started', 'time': env.now})

    def record_job_end(self, job: Job, env: simpy.Environment):
        self.job_events.append({'job': job.name, 'event': 'ended', 'time': env.now})

    def record_job_submission(self, job: Job, env: simpy.Environment):
        self.job_events.append({'job': job.name, 'event': 'submitted', 'time': env.now})

    def record_energy(self, node: Node):
        self.energy_usage.append({'node': node.name, 'energy': node.energy_consumption})

    def record_utilization(self, env: simpy.Environment, cluster: Cluster):
        total_gpus = sum(node.gpus_total for node in cluster.nodes)
        total_cpus = sum(node.cpus_total for node in cluster.nodes)
        total_mem = sum(node.memory_total for node in cluster.nodes)
        used_gpus = sum(node.gpus_total - node.gpus_available for node in cluster.nodes)
        used_cpus = sum(node.cpus_total - node.cpus_available for node in cluster.nodes)
        used_mem = sum(node.memory_total - node.memory_available for node in cluster.nodes)
        total_resources = total_gpus + total_cpus + total_mem
        used_resources = used_gpus + used_cpus + used_mem
        utilization = (used_resources / total_resources) * 100 if total_resources > 0 else 0
        self.utilization_samples.append({'time': env.now, 'utilization_percent': utilization})

    def report(self, output_file: str ="metrics_scheduler"):
        os.makedirs("metrics", exist_ok=True)

        # --- Job metrics ---
        job_fieldnames = ["job_name", "waiting_time_seconds", "submit_time", "start_time", "end_time"]
        jobs = set(wait['job'] for wait in self.waiting_times)
        jobs.update(event['job'] for event in self.job_events)
        job_metrics_file = f"{output_file}_jobs.csv"
        with open(os.path.join("metrics", job_metrics_file), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=job_fieldnames)
            writer.writeheader()
            for job in jobs:                
                row = {
                    "job_name": job,
                    "waiting_time_seconds": next((w['waiting_time'] for w in self.waiting_times if w['job'] == job), ''),
                    "submit_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'submitted'), ''),
                    "start_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'started'), ''),
                    "end_time": next((e['time'] for e in self.job_events if e['job'] == job and e['event'] == 'ended'), ''),
                }
                writer.writerow(row)

        # --- Node metrics ---
        node_fieldnames = ["node_name", "energy_consumed_kWh", "avg_utilization_percent", "avg_idle_time_seconds"]
        nodes = set(usage['node'] for usage in self.energy_usage)
        node_metrics_file = f"{output_file}_nodes.csv"

        # Collect utilization samples per node
        node_util_samples = {}
        node_idle_times = {}
        for sample in self.utilization_samples:
            # You may need to adapt this if you want per-node utilization
            # Here we assume cluster-wide, but you can extend your record_utilization to record per-node
            pass

        # Calculate average utilization and idle time per node
        # For demonstration, we'll set them to 0 unless you extend your utilization tracking
        with open(os.path.join("metrics", node_metrics_file), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=node_fieldnames)
            writer.writeheader()
            for node in nodes:
                energy = sum(usage['energy'] for usage in self.energy_usage if usage['node'] == node)
                avg_util = 0  # Extend your utilization tracking for per-node stats
                avg_idle = 0  # Extend your tracking for per-node idle time
                row = {
                    "node_name": node,
                    "energy_consumed_kWh": energy,
                    "avg_utilization_percent": avg_util,
                    "avg_idle_time_seconds": avg_idle
                }
                writer.writerow(row)

        # --- Cluster metrics ---
        cluster_fieldnames = ["avg_cluster_utilization_percent", "peak_cluster_utilization_percent", "min_cluster_utilization_percent"]
        cluster_metrics_file = f"{output_file}_cluster.csv"
        avg_util = sum(u['utilization_percent'] for u in self.utilization_samples) / len(self.utilization_samples) if self.utilization_samples else 0
        peak_util = max((u['utilization_percent'] for u in self.utilization_samples), default=0)
        min_util = min((u['utilization_percent'] for u in self.utilization_samples), default=0)
        with open(os.path.join("metrics", cluster_metrics_file), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cluster_fieldnames)
            writer.writeheader()
            writer.writerow({
                "avg_cluster_utilization_percent": avg_util,
                "peak_cluster_utilization_percent": peak_util,
                "min_cluster_utilization_percent": min_util
            })

        logger.info(f"Metrics exported to 'metrics/' as jobs, nodes, and cluster CSV files.")