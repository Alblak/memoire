# task_scheduler.py
"""Planificateur de tâches pour rappels automatiques"""

import threading
import time

class TaskScheduler:
    def __init__(self, app):
        self.app = app
        self.tasks = []
    
    def add_job(self, func, interval, unit='hours'):
        """Ajoute une tâche planifiée"""
        def run():
            while True:
                time.sleep(self._get_seconds(interval, unit))
                try:
                    func()
                except Exception as e:
                    print(f"Erreur tâche planifiée: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def start(self):
        """Démarre le planificateur"""
        pass
    
    def _get_seconds(self, interval, unit):
        if unit == 'hours':
            return interval * 3600
        elif unit == 'minutes':
            return interval * 60
        return interval