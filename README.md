# AISchedLab — AI Scheduling Simulator Lab for GPU Clusters
AISchedLab is a lightweight, extensible simulation framework for evaluating and comparing scheduling algorithms in heterogeneous GPU/CPU cluster environments. It is built with research and reproducibility in mind, providing a controlled lab setting to simulate realistic workload traces, cluster architectures, and resource allocation policies.

### YAML-Based Cluster & Job Definitions
Define workloads and cluster topologies using clear, human-readable configuration files.

### Power-Aware Simulation
Track node-level energy consumption over time, enabling analysis of energy efficiency across scheduling strategies.

### Reproducible Experimentation
Run consistent simulations via CLI or scripting, enabling comparative studies between scheduling approaches.

### Example Use Cases
- Academic experiments on HPC/AI job scheduling strategies
- Energy-aware workload placement analysis
- Evaluation of GPU cluster utilization and fairness
- Simulating the impact of queue time, node specs, and job mix

---

## Features

- **Cluster and Job Modeling:** Define clusters and jobs using simple YAML files.
- **Pluggable Scheduling Algorithms:** Easily extend or swap scheduling strategies (FIFO included).
- **Energy and Resource Tracking:** Monitor node utilization and energy consumption.
- **CLI Tool:** Run simulations and collect logs via a command-line interface.
- **Extensible:** Designed for researchers and developers to add new strategies and metrics.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- [pip](https://pip.pypa.io/en/stable/)
- (Recommended) [virtualenv](https://virtualenv.pypa.io/en/latest/)

### Clone the Repository

```sh
git clone https://github.com/Chrimetz/aischedlab.git
cd aischedlab

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install . --force-reinstall
```

---

## Creating YAML Files

### Cluster YAML

You can define your cluster nodes in `input/cluster.yaml`.  
There are two ways to define nodes:

**1. Single Node Example:**
```yaml
nodes:
  - name: node01
    gpus_total: 2
    cpus_total: 8
    memory_total: 32
    gpus_available: 2
    cpus_available: 8
    memory_available: 32
    power_idle: 150.0   # Watts in idle state
    power_active: 500.0 # Watts in active state
```

**2. Multiple Identical Nodes Using a Pattern:**
```yaml
nodes:
  - name_pattern: node_[0-9]
    gpus_total: 4
    cpus_total: 16
    memory_total: 64
    gpus_available: 4
    cpus_available: 16
    memory_available: 64
    power_idle: 120.0
    power_active: 350.0
```
This will create nodes named `node_0`, `node_1`, ..., `node_9` with identical resources.

You can mix both styles in the same file.

---

### Jobs YAML

Define jobs to be scheduled in `input/jobs.yaml`:

```yaml
- name: job_001
  submit_time: 0
  duration: 0.5
  gpus: 1
  cpus: 1
  memory: 2
- name: job_002
  submit_time: 1
  duration: 1
  gpus: 1
  cpus: 2
  memory: 4
# ... more jobs ...
```

- `submit_time`: When the job is submitted (simulation time units, e.g., hours).
- `duration`: How long the job runs (same units as submit_time).
- `gpus`, `cpus`, `memory`: Resource requirements for the job.

---

## Usage

### Run a Simulation

Use the CLI tool to run a simulation:

```sh
aischedlab --cluster=path/to/cluster.yaml --jobs=path/to/jobs.yaml
```

All logs (including simulation summary) are written to a timestamped log file (e.g., `ai_sched_lab_YYYYMMDD_HHMMSS.log`) in the current directory.

### Example PowerShell Script

You can automate the experiment with a script like:

```powershell
.venv\Scripts\Activate.ps1
pip install . --force-reinstall
aischedlab --cluster=.\input\cluster.yaml --jobs=.\input\jobs.yaml
```

---

## Project Structure

```
src/
  core/
    cli/
      run_simulation.py      # CLI entry point
    models.py                # Data models for Job, Node, Cluster
    simengine.py             # Simulation engine
    strategies/
      fifo.py                # FIFO scheduling strategy
    yaml_loader.py           # YAML loading utilities
pyproject.toml               # Build and dependency configuration
README.md                    # This file
```

---

## Extending AISchedLab

- **Add new scheduling strategies:** Implement a new class in `src/core/strategies/` following the interface in `fifo.py`.
- **Add new metrics or outputs:** Extend `simengine.py` or add new logging/statistics modules.

---

## License

This project is licensed under the Apache-2.0 License.

---

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub.