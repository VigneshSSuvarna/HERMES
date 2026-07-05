import asyncio
from core.orchestrator import HermesOrchestrator

def main():
    orchestrator = HermesOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        print("\n[System]: HERMES powering down systems smoothly. Goodbye, Sir.")

if __name__ == "__main__":
    main()