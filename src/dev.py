import sys
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

APP_FILE = "main.py"

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.process = None
        self.restart_app()

    def restart_app(self):
        if self.process:
            self.process.kill()
        self.process = subprocess.Popen([sys.executable, APP_FILE])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"==== Detected change in {event.src_path}, restarting app... ==== ")
            self.restart_app()

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    print("==== Watching for changes... Press CTRL+C to stop. ==== ")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n ==== Stopping auto-reload... ====")
        observer.stop()
    observer.join()
