import argparse
from core.simengine import SimulationEngine
from core.yaml_loader import load_jobs, load_cluster

def main():
    parser = argparse.ArgumentParser(description="Run a simulation with a specified cluster and jobs.")
    parser.add_argument('--cluster', type=str, required=True, help='Path to the cluster YAML file.')
    parser.add_argument('--jobs', type=str, required=True, help='Path to the jobs YAML file.')
    
    args = parser.parse_args()
    
    # Load cluster and jobs from YAML files
    cluster = load_cluster(args.cluster)
    jobs = load_jobs(args.jobs)
    
    # Create and run the simulation engine
    sim_engine = SimulationEngine(cluster=cluster, jobs=jobs)
    sim_engine.run()

if __name__ == "__main__":
    main()