import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("       YouTube Audio Splitter - Local Full Stack Launcher")
    print("=" * 60)

    project_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_dir, "frontend")
    venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")

    if not os.path.exists(venv_python):
        venv_python = sys.executable

    print("\n[1/2] Starting FastAPI Backend API on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen([
        venv_python, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000", "--reload"
    ], cwd=project_dir)

    time.sleep(2)

    print("[2/2] Starting React UI Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen([
        "npm.cmd", "run", "dev"
    ], cwd=frontend_dir, shell=True)

    print("\n" + "=" * 60)
    print("  🚀 Application is live!")
    print("  ► Open Web UI: http://localhost:5173")
    print("  ► API Backend: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("  Press Ctrl+C to stop both servers.\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
