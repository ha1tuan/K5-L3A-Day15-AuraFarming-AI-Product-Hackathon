import os
import sys
import tempfile

# test không ghi vào codebase/backend/var/trips.sqlite thật
os.environ.setdefault("TRIPS_DB", os.path.join(tempfile.mkdtemp(prefix="trips-test-"), "trips.sqlite"))

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
import _paths  # noqa: E402,F401
