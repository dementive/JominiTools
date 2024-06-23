import os
import subprocess
import shlex

class PluginManager:
    def __init__(self, path_to_repository: str, repository_url: str):
        self.path_to_repository = path_to_repository
        self.repository_url = repository_url

    def auto_update_plugin(self, branch="main"):
        normalized_path = os.path.normpath(self.path_to_repository)
        print("AUTO UPDATING THE PLUGINIGSDHJIGHNSDIOGJKILDSJGFOIDSJGIODSJGIODSJIOJGIOSDJG")
        # Check if the directory exists and is a git repository
        if not os.path.isdir(os.path.join(normalized_path, ".git")):
            print(f"JominiTools: {normalized_path} does not exist or is not a git repository.")
            return

        print(f"FETCHING FROM: {normalized_path}")
        print(f"PATH: {normalized_path} IS: {'exists' if os.path.exists(normalized_path) else 'does not exist'}")

        try:
            # Use shlex.split() to handle command arguments correctly
            subprocess.run(shlex.split("git -C {} fetch".format(normalized_path)), check=True)
            subprocess.run(shlex.split("git -C {} checkout {}".format(normalized_path, branch)), check=True)
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to switch to the {branch} branch: {e}")
            return

        try:
            subprocess.run(shlex.split("git -C {} pull".format(normalized_path)), check=True)
            print(f"JominiTools: Pulled changes for {normalized_path}")
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to update the {branch} branch: {e}")
