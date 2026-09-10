# Runs checks in a clean environment.
#
# This machine sources a ROS 2 (Jazzy) setup in .bashrc, which puts
# /opt/ros/... on PYTHONPATH and registers pytest entry-point plugins that
# fail to import without the full ROS stack. `env -u PYTHONPATH` and
# PYTEST_DISABLE_PLUGIN_AUTOLOAD keep this project's checks isolated from that.

PY := .venv/bin/python
CLEAN_ENV := env -u PYTHONPATH -u ROS_DISTRO PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

.PHONY: venv test typecheck check

venv:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install pytest mypy

test:
	$(CLEAN_ENV) $(PY) -m pytest

typecheck:
	env -u PYTHONPATH $(PY) -m mypy

check: test typecheck
