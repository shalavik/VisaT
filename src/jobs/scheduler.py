from __future__ import annotations
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from threading import RLock


class SchedulerManager:
    _instance: SchedulerManager | None = None
    _lock = RLock()

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()
        self.started = False

    @classmethod
    def instance(cls) -> SchedulerManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = SchedulerManager()
        return cls._instance

    def start(self) -> None:
        if not self.started:
            self.scheduler.start()
            self.started = True

    def shutdown(self) -> None:
        if self.started:
            self.scheduler.shutdown()
            self.started = False

    def register_interval_job(self, job_id: str, func, seconds: int, replace_existing: bool = True, **kwargs):
        self.scheduler.add_job(
            func=func,
            trigger=IntervalTrigger(seconds=seconds),
            id=job_id,
            replace_existing=replace_existing,
            **kwargs,
        )

    def remove_job(self, job_id: str) -> None:
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass

    def get_status(self):
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': str(job.next_run_time) if job.next_run_time else None
            })
        return {
            'started': self.started,
            'jobs': jobs
        }
