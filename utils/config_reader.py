from typing import Dict


def read_config_file(file: str) -> Dict:
    valid = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT",
        "OUTPUT_FILE", "PERFECT"
    ]
    optional = ["SEED", "ALGORITHM"]
    algos = ["DFS", "PRIME"]
    try:
        with open(file, "r") as read_lines:
            config = read_lines.readlines()
            if len(config) == 0:
                print("Empty config file!, give me some real data ...")
                return {}
            config_file = {}
            for line in config:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.count("=") != 1:
                    print("Invalid Syntax (must be exactly: ‘KEY=VALUE‘)",
                          line)
                    return {}
                if "=" not in line:
                    print(f"Invalid line: {line}")
                    return {}
                key, value = line.split("=", 1)
                key = key.strip().upper()
                value = value.strip()
                try:
                    if key in ["WIDTH", "HEIGHT", "SEED"]:
                        value = int(value)
                    elif key in ["ENTRY", "EXIT"]:
                        value = tuple(map(int, value.split(",")))
                    elif key == "PERFECT":
                        value = value.lower() == "true"
                    elif key == "ALGORITHM" and not value:
                        value = "DFS"
                    elif "ALGORITHM" not in config_file:
                        config_file["ALGORITHM"] = "DFS"
                    if key == "ALGORITHM":
                        value = value.upper()
                        if value not in algos:
                            print("Invalid algorithm")
                            return {}
                    elif key == "OUTPUT_FILE":
                        try:
                            with open(value, "w"):
                                pass
                        except Exception:
                            print("Problem with OUTPUT_FILE",
                                  "please check existance and"
                                  "permissions and path!")
                            return {}
                except Exception as e:
                    print(f"Invalid value for {key}: {value} ({e})")
                    return {}
                config_file[key] = value
            for key in valid:
                if key.upper() not in config_file:
                    print(f"Missing mandatory key: {key}")
                    return {}
            for key in config_file:
                if key not in valid and key not in optional:
                    print(f"Unknown key: {key}, ")
                    return {}
            return config_file
    except FileNotFoundError:
        print("No config file found, make one please!")
    except PermissionError:
        print("Check config file permissions please!")
    return {}


print(read_config_file("config.txt"))
