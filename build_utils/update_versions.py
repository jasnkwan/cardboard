import re
import json
import os
import subprocess


def update_pyproject_toml(version, file):
    """
    Update the version number in pyproject.toml
    """
    # Update pyproject.toml with the version
    with open(file, 'r') as f:
        toml_content = f.read()

    # Use regex to find and replace the version
    toml_content = re.sub(r'version = "[\d.]+"', f'version = "{version}"', toml_content)

    # Write the updated pyproject.toml file
    with open(file, 'w') as f:
        f.write(toml_content)

def update_package_json(version, file):
    """
    Update the version number in package.json
    """
    # Update package.json with the version
    with open(file, 'r') as f:
        package_json = json.load(f)

    # Update the version in package.json
    package_json['version'] = version

    # Write the updated package.json file
    with open(file, 'w') as f:
        json.dump(package_json, f, indent=2)


if __name__ == "__main__":
    # Configure paths
    script_dir = os.path.dirname(__file__)
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    ui_dir = os.path.join(project_dir, "cardboard_ui")

    version_txt = os.path.join(project_dir, "VERSION")
    pyproject_toml = os.path.join(project_dir, "pyproject.toml")
    package_json = os.path.join(ui_dir, "package.json")

    # Load the version from the VERSION file
    with open(version_txt) as version_file:

        version = version_file.read().strip()
        
        print(f"Updating version to {version}...")
        print(F"")
        print(f"  version        = {version}")
        print(f"  pyproject.toml = {pyproject_toml}")
        print(f"  package.json   = {package_json}")
        print(f"")
        update_pyproject_toml(version, pyproject_toml)
        update_package_json(version, package_json)

        # Commit files to git
        pyproject_toml_rel = os.path.relpath(pyproject_toml, project_dir)
        package_json_rel = os.path.relpath(package_json, project_dir)
        version_rel = os.path.relpath(version_txt, project_dir)

        print(f"Commiting updated pyproject.toml and package.json to git...")
        print(f"")

        commit_msg = f"Update version to {version}"
        git_add = f"git add {pyproject_toml_rel} {package_json_rel} {version_rel}"
        git_commit = f"git commit -m 'Update version to {version}'"
        
        print(f"git_add={git_add}")
        subprocess.check_call(git_add, shell=True, cwd=project_dir)

        print(f"git_commit={git_commit}")
        subprocess.check_call(git_commit, shell=True, cwd=project_dir)
