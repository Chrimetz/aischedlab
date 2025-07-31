from aischedlab.core.models import Cluster, Node, Job
from aischedlab.dse.job_generator import JobGenerator
from aischedlab.core.simengine import SimulationEngine
from aischedlab.core.base_scheduler import BaseScheduler

class DesignSpaceExplorer:
    def __init__(self, clusters: list[Cluster], jobs: list[Job] = None, schedulers: list = None):
        """
        Initialize the DesignSpaceExplorer with clusters, jobs, and schedulers.
        """
        self.clusters = clusters
        self.schedulers = schedulers

        if jobs:
            self.jobs = jobs
        else:
            job_gen = JobGenerator(
                num_jobs_range=(10, 50),
                submit_time_range=(0, 100),
                duration_range=(5, 20),
                gpu_range=(1, 4),
                cpu_range=(1, 8),
                memory_range=(1024, 8192)
            )
            self.jobs = job_gen.generate_jobs()

    def explore(self):
        # Placeholder for exploration logic
        print("Exploring design space...")
        for cluster in self.clusters:
            for scheduler in self.schedulers:
                print(f"Running simulation for cluster {cluster} with scheduler {scheduler.__name__}")
                self.run_simulation(cluster, scheduler)
            
    def run_simulation(self, cluster: Cluster, scheduler_cls: BaseScheduler):
        """
        Run a simulation with the given cluster and scheduler class.
        """
        sim_engine = SimulationEngine(
            cluster=cluster,
            jobs=self.jobs,
            scheduler_cls=scheduler_cls
        )
        sim_engine.run()
        sim_engine.print_summary()
