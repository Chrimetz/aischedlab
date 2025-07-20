import argparse
import logging
from datetime import datetime
from core.simengine import SimulationEngine
from core.yaml_loader import load_jobs, load_cluster

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
    parser.add_argument('--scheduler', type=str, choices=['fifo', 'sjf'], default='fifo',
                        help='Scheduling strategy to use (default: fifo).')
    
    args = parser.parse_args()
    
    # Load cluster and jobs from YAML files
    cluster = load_cluster(args.cluster)
    jobs = load_jobs(args.jobs)
    
    if args.scheduler == 'fifo':
        from core.strategies.fifo import FIFOScheduler
        scheduler_cls = FIFOScheduler
    elif args.scheduler == 'sjf':
        from core.strategies.sjf import SJFJobScheduler
        scheduler_cls = SJFJobScheduler

    # Create and run the simulation engine
    sim_engine = SimulationEngine(cluster=cluster, jobs=jobs, scheduler_cls=scheduler_cls)
    sim_engine.run()

if __name__ == "__main__":
    main()