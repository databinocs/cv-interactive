import yaml

def load_weights():
    try:
        with open("weights.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
