from typing import Dict


def read_config_file(file: str) -> Dict:
    try:
        with open(file, "r") as read_lines:
            valid = [
                "WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT", "ALGORITHM"
            ]
            config = read_lines.readlines()
            if len(config) == 0:
                print("Empty config file!, give me some real data ...")
                return {}
            config_file = {}
            for line in config:
                line.strip()
                if not line or line.startswith('#'):
                    continue
                if "=" not in line:
                    print(f"Invalid line: {line}")
                    return {}
                key, value = line.split('=')
                key = key.upper()
                value = value.strip()
                key, value = line.split("=", 1)
                key = key.strip().upper()
                value = value.strip()
                if key not in valid:
                    print(f"Unknown key: {key}")
                    return {}
                try:
                    if key in ["WIDTH", "HEIGHT"]:
                        value = int(value)
                    elif key in ["ENTRY", "EXIT"]:
                        value = tuple(map(int, value.split(",")))
                    elif key == "PERFECT":
                        value = value.lower() == "true"
                    elif key == "ALGORITHM" and not value:
                        value = "DFS"
                except Exception as e:
                    print(f"Invalid value for {key}: {value} ({e})")
                    return {}
                config_file[key] = value
            for key in valid:
                if key.upper() not in config_file:
                    print(f"Missing mandatory key: {key}")
                    return {}
            return config_file
    except FileNotFoundError:
        print("No config file found, make one please!")
    except PermissionError:
        print("Check config file permissions please!")
    return {}


print(read_config_file("config.txt"))