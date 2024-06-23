"""
Class to handle generic tasks related to maintenance and updating of a sublime plugin
"""

import os
import subprocess


class PluginManager:
    def __init__(self, path_to_repository: str, repository_url: str):
        self.path_to_repository = path_to_repository
        self.repository_url = repository_url

    def auto_update_plugin(self, branch="main"):
        # Pull the latest changes from git to update a plugin on a certain branch
        if not os.path.isdir(os.path.join(self.path_to_repository, ".git")):
            print(f"JominiTools: {self.path_to_repository} is not a git repository.")
            return

        try:
            subprocess.run(["git", "-C", self.path_to_repository, "fetch"], check=True)
            subprocess.run(
                ["git", "-C", self.path_to_repository, "checkout", branch], check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to switch to the {branch} branch: {e}")
            return

        try:
            subprocess.run(["git", "-C", self.path_to_repository, "pull"], check=True)
            print(f"JominiTools: Pulled changes for {self.path_to_repository}")
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to update the {branch} branch: {e}")
