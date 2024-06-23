import os
import subprocess
import shlex

class PluginManager:
    def __init__(self, path_to_repository: str, repository_url: str):
        self.path_to_repository = path_to_repository
        self.repository_url = repository_url

    def auto_update_plugin(self, branch="main"):
        # Ensure the path is correctly formatted for the OS
        normalized_path = os.path.normpath(self.path_to_repository)

        # Check if the directory exists and is a git repository
        if not os.path.isdir(normalized_path):
            print(f"JominiTools: {normalized_path} does not exist or is not a git repository.")
            return

        try:
            # Attempt to run git commands
            subprocess.run(shlex.split("git -C {} checkout {}".format(normalized_path, branch)), check=True)
        except FileNotFoundError as e:
            print(f"JominiTools: Error: Could not find 'git'. Please ensure Git is installed and available in your PATH.")
            return
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to switch to the {branch} branch: {e}")

        try:
            subprocess.run(shlex.split("git -C {} fetch".format(normalized_path)), check=True)
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to fetch from the {branch} branch: {e}")
            return

        try:
            subprocess.run(shlex.split("git -C {} pull".format(normalized_path)), check=True)
            print(f"JominiTools: Pulled changes for {normalized_path}")
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to pull from the {branch} branch: {e}")
