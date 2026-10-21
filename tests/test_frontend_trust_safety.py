"""
Runs the frontend trust-and-safety tests (src/trustSafety.test.js) with Node's built-in test runner.
They cover the removed fabricated claims in src/App.jsx, the backend-unavailable state, the status
model and jurisdiction reconciliation. Skipped only if Node.js is not installed.
"""

import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not installed")
def test_frontend_trust_safety_node_suite():
    proc = subprocess.run(["node", "--test", "--test-reporter=tap", os.path.join("src", "trustSafety.test.js")],
                          cwd=ROOT, capture_output=True, text=True, timeout=120)
    summary = [l for l in proc.stdout.splitlines() if l.startswith(("# pass", "# fail", "not ok"))]
    assert proc.returncode == 0, "\n".join(summary) or proc.stderr[-2000:]
    assert "# fail 0" in proc.stdout
