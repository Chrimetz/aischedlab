import argparse
import logging
from datetime import datetime
from aischedlab.core.simengine import SimulationEngine
from aischedlab.core.yaml_loader import load_jobs, load_cluster
from aischedlab.core.strategies import BackfillScheduler, SJFJobScheduler, FIFOScheduler

log_filename = f"ai_sched_lab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_filename, mode='w'),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description="Run a simulation with a specified cluster and jobs.")
    parser.add_argument('--cluster', type=str, required=True, help='Path to the cluster YAML file.')
    parser.add_argument('--jobs', type=str, required=True, help='Path to the jobs YAML file.')
    parser.add_argument('--scheduler', type=str, choices=['fifo', 'sjf', 'backfill'], default='fifo',
                        help='Scheduling strategy to use (default: fifo).')
    
    args = parser.parse_args()
    
    # Load cluster and jobs from YAML files
    cluster = load_cluster(args.cluster)
    jobs = load_jobs(args.jobs)
    
    if args.scheduler == 'fifo':
        scheduler_cls = FIFOScheduler
    elif args.scheduler == 'sjf':
        scheduler_cls = SJFJobScheduler
    elif args.scheduler == 'backfill':
        scheduler_cls = BackfillScheduler

    # Create and run the simulation engine
    sim_engine = SimulationEngine(cluster=cluster, jobs=jobs, scheduler_cls=scheduler_cls)
    sim_engine.run()

if __name__ == "__main__":
    main()