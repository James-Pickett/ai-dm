import yaml

def load(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        return config

