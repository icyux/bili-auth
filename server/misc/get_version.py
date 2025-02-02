import os
import subprocess

def get_version():
	version = os.getenv("VERSION")
	if version is not None:
		return version

	try:
		version = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL, text=True).strip()
		return version
	except (FileNotFoundError, subprocess.CalledProcessError):
		pass

	return None
