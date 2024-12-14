import os
import yaml

env_vars_file_path = os.path.join(
    os.path.dirname(__file__), 
    '../env_vars.yml'
    )
with open(env_vars_file_path, 'r') as vars_file:
    data = yaml.safe_load(vars_file)
    env_vars = data['env_vars']['common']
