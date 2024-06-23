"""
Class to handle generic tasks related to maintenance and updating of a sublime plugin
"""

import os
import subprocess


class PluginManager:
    def auto_update_plugin(self, path, branch="main"):
        # Pull the latest changes from git to update a plugin on a certain branch
        if not os.path.isdir(os.path.join(path, ".git")):
            print(f"JominiTools: {path} is not a git repository.")
            return

        try:
            subprocess.run(["git", "-C", path, "fetch"], check=True)
            subprocess.run(["git", "-C", path, "checkout", branch], check=True)
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to switch to the {branch} branch: {e}")
            return

        # Pull the latest changes
        try:
            subprocess.run(["git", "-C", path, "pull"], check=True)
            print(f"JominiTools: Pulled changes for {path}")
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to update the {branch} branch: {e}")

    def clone_and_update_repo(self, repo_url, destination_dir):
        # Check if the.git directory exists in the destination directory, if it doens't clone it and switch to main.
        if not os.path.exists(os.path.join(destination_dir, ".git")):
            print(f"Cloning repository {repo_url} into {destination_dir}...")
            subprocess.run(["git", "clone", repo_url, destination_dir], check=True)

        subprocess.run(["git", "-C", destination_dir, "checkout", "main"], check=True)
        subprocess.run(["git", "-C", destination_dir, "pull"], check=True)


# Example usage
# folder_path1 = sublime.packages_path() + f'{os.sep}Victoria3Tools'
# sublime.set_timeout_async(
# 	lambda: auto_update_plugin(folder_path1), 0
# )
# folder_path = sublime.packages_path() + f'{os.sep}ImperatorTools'
# sublime.set_timeout_async(
# 	lambda: auto_update_plugin(folder_path), 0
# )
