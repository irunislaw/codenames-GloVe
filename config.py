import os 
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)
            print("Configuration loaded successfully from", CONFIG_PATH)
            return user_config
        
def save_config(path):
    try:
        with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(settings, f, sort_keys=False, default_flow_style=False)
        print("Configuration saved successfully to", path)
        return True
    except Exception as e:
        print(f"Failed to save config.yaml {e}")
        return False
settings = load_config()

