"""
David AI Assistant - Main Entry Point (Web GUI Mode)
"""
import sys
import os

# Force UTF-8 output on Windows to avoid emoji/Unicode crashes
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def check_dependencies():
    """Check core dependencies are available."""
    missing = []
    for mod, pkg in [
        ("sounddevice", "sounddevice"),
        ("numpy",       "numpy"),
        ("whisper",     "openai-whisper"),
        ("requests",    "requests"),
        ("rich",        "rich"),
        ("fastapi",     "fastapi"),
        ("uvicorn",     "uvicorn"),
        ("ollama",      "ollama"),
    ]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("ERROR: Missing dependencies:")
        for m in missing:
            print(f"  pip install {m}")
        return False
    return True


def validate_setup():
    """Validate Ollama + ffplay."""
    from core.config import validate_config
    from ai.llm import check_ollama_connection
    errors = list(validate_config())

    if not check_ollama_connection():
        errors.append("Ollama is not running -- start it with: ollama serve")

    # Check ffplay (needed for cloud TTS)
    try:
        import subprocess
        r = subprocess.run(["ffplay", "-version"], capture_output=True, timeout=2)
        if r.returncode != 0:
            os.environ["TTS_ENGINE"] = "local"
    except Exception:
        os.environ["TTS_ENGINE"] = "local"

    return errors


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    print("=" * 50)
    print("  David AI Assistant  (Web UI mode)")
    print("=" * 50)

    if not check_dependencies():
        sys.exit(1)

    print("\nChecking setup...")
    errors = validate_setup()
    if errors:
        print("\n[!] Issues found:")
        for e in errors:
            print(f"  * {e}")
        ans = input("\nContinue anyway? (y/N): ")
        if ans.lower() != 'y':
            sys.exit(1)
    else:
        print("[OK] All checks passed!\n")

    print("Starting David AI -- accessible at http://0.0.0.0:8001 ...\n")
    print("  Local:    http://127.0.0.1:8001")
    print("  Network:  http://192.168.56.1:8001  (for mobile app)\n")
    from web.server import run_web
    run_web(host="0.0.0.0", port=8001, open_browser=False)
