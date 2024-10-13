import toml

# Read requirements.txt
with open("requirements.txt", "r") as f:
    dependencies = f.read().strip().splitlines()

# Load the existing pyproject.toml
pyproject = toml.load("pyproject.toml")

# Update the dependencies
pyproject['project']['dependencies'] = dependencies

# Write the updated pyproject.toml
with open("pyproject.toml", "w") as f:
    toml.dump(pyproject, f)
