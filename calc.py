from logging import config
import os
import sys
import ast
import json
import operator
import pyfiglet
import requests
from packaging import version


__version__ = "v2.9"

# Define functions for Auto-Updates.
def get_latest_release_tag():
    try:
        url = "https://api.github.com/repos/cells-OSS/pyculator/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"].lstrip("v")
    except Exception as e:
        print("Failed to check for updates:", e)
        return __version__.lstrip("v")


def is_update_available(current_version):
    latest = get_latest_release_tag()
    return version.parse(latest) > version.parse(current_version.lstrip("v"))


def download_latest_script():
    latest_version = get_latest_release_tag()
    filename = f"pyculator-v{latest_version}.py"
    url = "https://raw.githubusercontent.com/cells-OSS/pyculator/main/calc.py"
    response = requests.get(url)
    lines = response.text.splitlines()
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
    print(
        f"Current version: {__version__}, Latest: v{get_latest_release_tag()}")
    print(
        f"Downloaded update as '{filename}'. You can now safely delete the old version.")

    input("Press Enter to exit...")
    exit()

# If the script is running on Windows, use roaming appdata, else use ~/.config.
if os.name == "nt":
    config_dir = os.path.join(os.getenv("APPDATA"), "pyculator")
else:
    config_dir = os.path.expanduser("~/.config/pyculator")

# If the config directory is not there, create it.
os.makedirs(config_dir, exist_ok=True)

config_path = os.path.join(config_dir, "config.json")

# Loads the config file.
def load_config():
    path = os.path.join(config_dir, "config.json")
    if not os.path.exists(path):
        default = {"auto_updates": True, "figlet_welcome": False}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Saves the config file.
def save_config(config):
    with open(os.path.join(config_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# Toggles auto-updates.
def toggle_auto_updates():
    config = load_config()
    
    config["auto_updates"] = not config.get("auto_updates", True)
    
    save_config(config)
    print(f"Auto updates are now {'ON' if config['auto_updates'] else 'OFF'}")
# Toggles figlet welcome message.
def toggle_figlet():
    config = load_config()
    
    config["figlet_welcome"] = not config.get("figlet_welcome", False)
    
    save_config(config)
    print(f"Figlet welcome message is now {'ON' if config['figlet_welcome'] else 'OFF'}")


welcomeMessage_config_path = os.path.join(config_dir, "welcome_message.conf")

# Changes the welcome message if changed.
if os.path.exists(welcomeMessage_config_path):
    with open(welcomeMessage_config_path, "rb") as configFile:
        welcomeMessage = configFile.read().decode()
else:
    welcomeMessage = """
    ===============WELCOME===============
    """

# Loads the config file.
config = load_config()

# If figlet welcome message is enabled, figlet the welcome message.
if config["figlet_welcome"]:
    welcomeMessage = pyfiglet.figlet_format(welcomeMessage)

# If auto-updates are enabled, check for updates.
if config["auto_updates"]:
    if is_update_available(__version__):
        print("A new version of Pyculator is available!")
        user_input = input(
            "Would you like to download the latest version? (y/n): ").strip().lower()
        if user_input == "y":
            download_latest_script()


menu = """

1 = Basic math expressions
2 = Find the given exponent of the given number
3 = Round a Number
4 = Find the given percentage of a number
5 = Finding the possible base(s) and the exponent(s) of the given number
6 = Finding the smallest possible n-th root of the given number
7 = Find the given numbers multipliers
8 = Settings

TIP: If you want to come back to this menu at any time, just type "back"
"""
print(welcomeMessage, menu)

chooseOption = int(
    input("Which option would you like to choose(1/2/3/4/5/6/7/8)?: "))

while True:

# Code used for adding, subtracting, multiplying, and dividing.
    if chooseOption == 1:
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.floordiv,
            ast.Mod: operator.mod,
            ast.FloorDiv: operator.floordiv,
            ast.Pow: operator.pow,
        }

        def safe_eval(expr):

            node = ast.parse(expr, mode="eval").body

            def _eval(node):
                if isinstance(node, ast.BinOp):
                    if type(node.op) not in operators:
                        raise ValueError("Operator not allowed")

                    left = _eval(node.left)
                    right = _eval(node.right)

                    if isinstance(node.op, ast.Div):

                        quotient = left // right
                        remainder = left % right
                        return f"{left} ÷ {right} = {quotient} remainder {remainder}"

                    return operators[type(node.op)](left, right)

                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        return node.value
                    else:
                        raise ValueError("Only numbers are allowed")

                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        return node.value
                    else:
                        raise ValueError("Only numbers are allowed")

                elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
                    return -_eval(node.operand)

                else:
                    raise ValueError("Expression not allowed")

            return _eval(node)

        while True:
            expr = input("> ")
            if expr == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            try:
                result = safe_eval(expr)
                print("=", result)
            except Exception as e:
                print("Error:", e)
                input("Press any key to restart...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

    # Code used for calculating the exponent of a number.
    if chooseOption == 2:
        firstInput = input("Base: ")

        if firstInput.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        base = float(firstInput)
        secondInput = input("Exponent: ")

        if secondInput.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        exponent = float(secondInput)
        print(">", base ** exponent)

    # Code used to round a number, there are plans to give it a calculation and then find the answer's rounded value.
    if chooseOption == 3:
        while True:
            userInput = input("> ")

            if userInput.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            toRound = float(userInput)
            print(">", round(toRound))

    # Code used to find the percentage of a number.
    if chooseOption == 4:
        while True:
            firstInput = input("Number: ")

            if firstInput.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            Number = float(firstInput)

            secondInput = input("Percentage: ")

            if secondInput.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            Percentage = float(secondInput)
            print(">", Percentage / 100 * Number)

    # Code used to find the possible base(s) and exponent(s) of a given number.
    if chooseOption == 5:
        while True:

            number = input("> ")
            found = False

            if number == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            number = int(number)

            for base in range(2, number + 1):
                for exponent in range(2, number + 1):
                    if base ** exponent == number:

                        print(f"{number} is: {base}^{exponent}")
                        found = True
                        break

                    if found:
                        break
            if not found:
                print(f"{number} cannot be expressed")

    # Code used to find the smallest possible n-th root of a given number.
    if chooseOption == 6:
        while True:
            num = input("Enter the number: ")

            if num == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            nInput = input("Enter the degree of the root: ")

            number = int(num)

            if nInput == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            n = int(nInput)

            a = 1
            b = number

            start = round(number ** (1/n))

            for i in range(start, 0, -1):
                if number % (i ** n) == 0:
                    a = i
                    b = number // (i ** n)
                    break

            if b == 1:
                print(f"{n}-th root of {number} = {a}")
            else:
                print(f"{n}-th root of {number} = {a} * {n}-th_root({b})")

    # Code used to find the multipliers of a given number.
    if chooseOption == 7:
        while True:
            userInput = input("> ")

            if userInput == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            num = int(userInput)
            for answer in range(1, num + 1):

                result = num / answer
                if result.is_integer():
                    print(result)

    # Code used for the settings interface.
    if chooseOption == 8:
        settingsMenu = """
    ===============SETTINGS===============

    1 = Change welcome message
    2 = Figlet welcome message
    3 = Reset welcome message
    4 = Change auto-update settings
    """
        print(settingsMenu)

        chooseSetting = input(
            "Which setting would you like to change(1/2/3/4)?: ")

        if chooseSetting.lower() == "back":
            os.execv(sys.executable, [sys.executable] + sys.argv)

        # Change the welcome message text.
        if chooseSetting == "1":
            new_welcomeMessage = input("New welcome message: ")
            config_path = os.path.join(config_dir, "welcome_message.conf")

            if new_welcomeMessage.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            with open(config_path, "wb") as configFile:
                configFile.write(new_welcomeMessage.encode())

            print("Changes saved successfully!")
            input("Press any key to restart...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        # Code for the figlet welcome message interface.
        if chooseSetting == "2":
            figletWelcome = """
        ===============FIGLET===============

        1 = Toggle figlet welcome message
        """

            print(figletWelcome)
            figletOption = input(
                "Which option would you like to choose(1)?: ")

            if figletOption.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)
            
            # Toggles the figlet welcome message.
            if figletOption == "1":
                toggle_figlet()

                print("Changes saved successfully!")
                input("Press any key to restart...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

        # Resets the welcome message to default by deleting the config file.
        if chooseSetting == "3":
            config_path = os.path.join(config_dir, "welcome_message.conf")

            if os.path.exists(config_path):
                os.remove(config_path)
                print("Changes saved successfully!")
                input("Press any key to restart...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

            else:
                print("You haven't changed the welcome message yet!")
                input("Press any key to restart...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

        # Code for the auto-update settings interface.
        if chooseSetting == "4":
            aUpdateMenu = """
    ===============AUTO-UPDATE===============

    1 = Toggle auto-updates
    """

            print(aUpdateMenu)
            aUpdateOption = input(
                "Which option would you like to choose(1)?: ")

            if aUpdateOption.lower() == "back":
                os.execv(sys.executable, [sys.executable] + sys.argv)

            # Toggles auto-updates.
            if aUpdateOption == "1":
                toggle_auto_updates()

                print("Changes saved successfully!")
                input("Press any key to restart...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            input("Invalid option. Press any key to restart...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        input("Invalid option. Press any key to restart...")
        os.execv(sys.executable, [sys.executable] + sys.argv)