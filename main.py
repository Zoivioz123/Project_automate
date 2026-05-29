import argparse
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, List

from nicegui import ui

# Init vars
platform_name = platform.system()
current_year = datetime.date.today().year


# Functions
def load_conf(conf_path):
    try:
        with open(conf_path, "r", encoding="utf8") as file:
            response = json.load(file)
            print(f"[INF] Loaded {args.config}")
            return response
    except Exception as err:
        print("[ERR] Unable to load config file: " + str(err))
        exit(1)


def open_folder(path: str) -> None:
    try:
        if platform_name == "Windows":
            os.startfile(path)
        elif platform_name == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"[WARN] Could not open folder: {e}")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.json",
        help="Path to json configuration path",
    )

    args, _ = parser.parse_known_args()
    return args


def create_offer(config: dict, offer_id: str, project_name: str, customer: str):
    if "/" in offer_id or "\\" in offer_id:
        ui.notify('Offer ID can\'t contain "/" or "\\"', type="negative")
        print('[ERR] Offer ID can\'t contain "/" or "\\"')
        return 1
    if "/" in project_name or "\\" in project_name:
        ui.notify('Project Name can\'t contain "/" or "\\"', type="negative")
        print('[ERR] Project Name can\'t contain "/" or "\\"')
        return 1
    if "/" in customer or "\\" in customer:
        ui.notify('Customer Name can\'t contain "/" or "\\"', type="negative")
        print('[ERR] Customer Name can\'t contain "/" or "\\"')
        return 1

    destination_path = config["folder_structure"].format(
        offers_path=config["offers_path"].rstrip("/"),
        customer=customer,
        year=current_year,
        offer_id=offer_id,
        project_name=project_name,
    )

    try:
        shutil.copytree(config["template_path"], destination_path)

        for rule in config["renames"]:
            source_relative = rule["src"].format(
                offer_id=offer_id, project_name=project_name
            )
            destination_relative = rule["dst"].format(
                offer_id=offer_id, project_name=project_name
            )

            full_source_path = os.path.join(destination_path, source_relative)
            full_destination_path = os.path.join(destination_path, destination_relative)

            if os.path.exists(full_source_path):
                os.rename(full_source_path, full_destination_path)
                print(f"[INF] Renamed: {source_relative} -> {destination_relative}")

            ui.notify("Project structure created successfully!", type="positive")

    except FileExistsError as err:
        ui.notify("This offer folder already exists!", type="negative")
    except Exception as err:
        ui.notify(f"Error: {str(err)}", type="negative")
        print(f"[ERR] {str(err)}")


def get_customers(offers_path):
    try:
        return sorted(
            e
            for e in os.listdir(offers_path)
            if os.path.isdir(os.path.join(offers_path, e))
        )
    except Exception:
        return []


def submit_form():
    if customer_selection.value == "[ Add New Customer ]":
        value = new_customer_input.value or ""
        customer = value.strip()
    else:
        customer = customer_selection.value

    if not customer or not offer_id_input.value or not project_name_input.value:
        ui.notify("Please fill in all fields!", type="warning")
        return

    offer_id = offer_id_input.value.strip() if offer_id_input.value else ""
    project_name = project_name_input.value.strip() if project_name_input.value else ""

    if not customer or not offer_id or not project_name:
        ui.notify("Please fill in all fields!", type="warning")
        return

    create_offer(
        config=config,
        offer_id=offer_id,
        project_name=project_name,
        customer=customer,
    )

    ui.notify(
        f"Creatied project for {customer} ({offer_id_input.value} - {project_name_input.value})",
        type="positive",
    )


def create_offer_gui(config):
    existing_customers = get_customers(config["offers_path"])
    customer_options = existing_customers + ["[ Add New Customer ]"]

    with ui.card().classes("w-96 p-4"):
        offer_id_input = ui.input(label="Offer ID", placeholder="e.g., 001").classes(
            "w-full"
        )
        project_name_input = ui.input(
            label="Project Name", placeholder="e.g., Project"
        ).classes("w-full")

        customer_selection = ui.select(
            options=customer_options,
            label="Select Customer",
            value=customer_options[0] if customer_options else None,
        ).classes("w-full")

        new_customer_input = (
            ui.input(label="New Customer Name", placeholder="Enter name...")
            .classes("w-full")
            .bind_visibility_from(
                customer_selection,
                "value",
                backward=lambda v: v == "[ Add New Customer ]",
            )
        )

        ui.button("Create Offer", on_click=submit_form).classes("w-full q-mt-md")

        return (
            offer_id_input,
            project_name_input,
            customer_selection,
            new_customer_input,
        )


# Main
args = get_args()
config = load_conf(args.config)

offer_id_input, project_name_input, customer_selection, new_customer_input = (
    create_offer_gui(config)
)

ui.run(reload=False)
