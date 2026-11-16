import sys

if len(sys.argv) > 1 and sys.argv[1] == "--check-python":
    from didactyx_engine.example_runner import main
else:
    from didactyx_engine.server import main

if __name__ == "__main__":
    raise SystemExit(main())
