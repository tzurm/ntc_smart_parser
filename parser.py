#!/usr/bin/env python3
import os
import json
import argparse
from datetime import datetime
import textfsm
import fnmatch
import re

TEMPLATE_DIR = os.path.normpath("./ntc-templates/templates")
PLATFORM = "cisco_ios"
COMMANDS_MAP_FILE = "commands_map.json"


def load_commands_map():
    if os.path.exists(COMMANDS_MAP_FILE):
        with open(COMMANDS_MAP_FILE) as f:
            return json.load(f)
    return {}


def map_command(filename: str, commands_map: dict):
    """
    Map filename to template command using wildcard patterns.
    """
    name = filename.lower().replace(".log", "")
    for template_name, patterns in commands_map.items():
        for p in patterns:
            if fnmatch.fnmatch(name, p.lower()):
                return template_name
    return None


def parse_file(filepath: str, rel_path: str, command: str):
    """
    Parse one log file with ntc-templates + TextFSM.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    if not lines:
        return []

    # Extract device name and IP if available in the first line
    first_line = lines[0].strip()
    m = re.match(r"(\S+)\s*\(([\d\.]+)\):", first_line)
    if m:
        device_name = m.group(1)
        device_ip = m.group(2)
        body_lines = lines[1:]
    else:
        device_name = "unknown"
        device_ip = "unknown"
        body_lines = lines

    # Clean irrelevant lines before parsing
    clean_lines = []
    for line in body_lines:
        l = line.strip()
        if not l:
            continue
        if l.lower().startswith(("sh", "show")):
            continue
        if "| no" in l.lower():
            continue
        if "device_name" in l.lower():
            continue
        clean_lines.append(line)
    raw_text = "".join(clean_lines)

    # Locate the matching template
    template_file = f"{PLATFORM}_{command.replace(' ', '_')}.textfsm"
    template_path = os.path.normpath(os.path.join(TEMPLATE_DIR, template_file))

    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return []  # no fallback

    print(f"Parsing file: {filepath}")
    print(f"Device: {device_name}, IP: {device_ip}")
    print(f"Command detected: {command}")
    print(f"Using template: {template_path}")

    records = []
    with open(template_path) as tf:
        fsm = textfsm.TextFSM(tf)
        parsed = fsm.ParseText(raw_text)

    for row in parsed:
        record = dict(zip(fsm.header, [str(v) for v in row]))
        record.update({
            "raw": " ".join([str(v) for v in row]),
            "source_file": rel_path,
            "device_name": device_name,
            "device_ip": device_ip,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        records.append(record)

    return records


def main():
    parser_arg = argparse.ArgumentParser(description="Parse ntc-templates logs recursively")
    parser_arg.add_argument("-i", required=True, help="Input folder")
    parser_arg.add_argument("-o", required=True, help="Output folder")
    args = parser_arg.parse_args()

    os.makedirs(args.o, exist_ok=True)
    commands_map = load_commands_map()
    records_by_command = {}

    for root, _, files in os.walk(args.i):
        for file in files:
            if not file.lower().endswith(".log"):
                continue

            full_path = os.path.normpath(os.path.join(root, file))
            rel_path = os.path.relpath(full_path, args.i)

            command = map_command(file, commands_map)
            if not command:
                print(f"No matching command pattern for file: {file}, skipping.\n")
                continue

            try:
                recs = parse_file(full_path, rel_path, command)
                if recs:
                    records_by_command.setdefault(command, []).extend(recs)
            except Exception as e:
                print(f"Error parsing {full_path}: {e}\n")

    # Save each command type into a separate JSON file
    for cmd, records in records_by_command.items():
        if not records:
            continue
        filename_safe = cmd.replace(" ", "_") + "_output.json"
        output_file = os.path.join(args.o, filename_safe)
        with open(output_file, "w") as f:
            json.dump(records, f, indent=2)
        print(f"{len(records)} records saved to {output_file}")


if __name__ == "__main__":
    main()
