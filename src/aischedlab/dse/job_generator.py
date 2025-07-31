from aischedlab.core.models import Job
import random

class JobGenerator:
    def __init__(self, num_jobs_range: tuple[int, int], submit_time_range: tuple[int, int], duration_range: tuple[int, int], gpu_range: tuple[int, int], cpu_range: tuple[int, int], memory_range: tuple[int, int]):
        self.num_jobs_range = num_jobs_range
        self.submit_time_range = submit_time_range
        self.duration_range = duration_range
        self.gpu_range = gpu_range
        self.cpu_range = cpu_range
        self.memory_range = memory_range

    def generate_jobs(self) -> list[Job]:
        jobs = []
        for _ in range(random.randint(*self.num_jobs_range)):  # Generate a random number of jobs
            job = Job(
                id=random.randint(1, 1000),
                name=f"Job-{random.randint(1, 100)}",
                resources={
                    "gpu": random.randint(*self.gpu_range),
                    "cpu": random.randint(*self.cpu_range),
                    "memory": random.randint(*self.memory_range),
                },
                runtime=random.randint(*self.duration_range),
            )
            jobs.append(job)
        return jobs