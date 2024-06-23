import os
import subprocess

class PluginManager:
    def __init__(self, path_to_repository: str, repository_url: str):
        self.path_to_repository = path_to_repository
        self.repository_url = repository_url

    def auto_update_plugin(self, branch="main"):
        normalized_path = os.path.normpath(self.path_to_repository)
        if not os.path.isdir(normalized_path):
            print(f"JominiTools: {normalized_path} does not exist or is not a git repository.")
            return

        startupinfo = None
        if os.name == 'nt': # Don't show command prompt window on windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            cmd = ["git", "-C", normalized_path, "checkout", branch]
            print(f"CHECKOUT with: {cmd}")
            subprocess.run(cmd, check=True, startupinfo=startupinfo)
        except FileNotFoundError as e:
            print(f"JominiTools: Error: Could not find 'git'. Please ensure Git is installed and available in your PATH.")
            return
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to switch to the {branch} branch: {e}")

        try:
            cmd = ["git", "-C", normalized_path, "fetch"]
            print(f"FETCH with: {cmd}")
            subprocess.run(cmd, check=True, startupinfo=startupinfo)
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to fetch from the {branch} branch: {e}")
            return

        try:
            cmd = ["git", "-C", normalized_path, "pull"]
            print(f"JominiTools: Pulled changes for {normalized_path}")
            subprocess.run(cmd, check=True, startupinfo=startupinfo)
        except subprocess.CalledProcessError as e:
            print(f"JominiTools: Failed to pull from the {branch} branch: {e}")