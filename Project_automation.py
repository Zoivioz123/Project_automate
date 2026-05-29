import os
import subprocess


def update_myself():
    print("Updating from Git")
    try:
        subprocess.run(["git", "fetch", "--all"], check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)

        if os.path.exists("requirements.txt"):
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

        print("Everything is up to date")
    except Exception as err:
        print(f"Unable to update: {err}")


def install_myself():
    print("Installing myself from Git")
    try:
        subprocess.run(
            ["git", "clone", "git@github.com:Zoivioz123/Project_automate.git"],
            check=True,
        )

        if os.path.exists("requirements.txt"):
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

        print("Everything is installed")
    except Exception as err:
        print(f"Unable to install: {err}")


if os.path.exists(".dev"):
    if os.path.exists(".dev"):
        print("Dev mode is enabled \nUpdate skiped")
        exit(0)
else:
    if os.path.exists(".git"):
        update_myself()
    else:
        install_myself()

os.system("python ./main.py")
