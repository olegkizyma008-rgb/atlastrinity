#!/usr/bin/env python3
"""CI helper: patch heavy setup operations to no-ops and run setup_dev.main() so the workflow can validate behavior quickly.

This is used by the CI job instead of an inline heredoc to keep the YAML valid and lint-friendly.
"""
import sys
from importlib import import_module

try:
    s = import_module("scripts.setup_dev")
    # Patch heavy operations to be no-ops so setup completes quickly in CI
    s.install_deps = lambda: True
    s.build_swift_mcp = lambda: True
    s.download_models = lambda: True
    s.check_services = lambda: True
    s.sync_configs = lambda: True

    # Run setup_main and exit accordingly
    try:
        s.main()
        print("setup_dev.py completed successfully")
        sys.exit(0)
    except SystemExit as e:
        # Propagate SystemExit for expected behavior in CI
        raise
    except Exception as e:
        print("setup_dev.py raised exception:", e)
        sys.exit(1)
except Exception as e:
    print("Failed to import/setup scripts.setup_dev:", e)
    sys.exit(1)
