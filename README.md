# NTC Log Parser

A Python CLI tool for parsing raw command outputs (Cisco IOS or other vendor) into structured JSON using [ntc-templates](https://github.com/networktocode/ntc-templates) and [TextFSM](https://github.com/google/textfsm).



## ✨ Features
- Recursive parsing of `.log` files from input directories (supports subfolders).
- Automatic command detection based on filename patterns.
- Per-command JSON output (all logs of the same command aggregated into one file).
- Metadata enrichment:  
  - `raw` → original record line  
  - `source_file` → relative path to the log file  
  - `device_name` and `device_ip` → extracted from the first line (`DeviceName (IP):`)  
  - `timestamp` → when the script ran (no seconds)  
- Cross-platform (tested on Linux & Windows).



## 📂 Folder Structure
project/
│
├── ntc-templates/ # Cloned NTC templates repo
│ └── templates/ # .textfsm template files
│
├── commands_map.json # Mapping of filenames → commands → templates
├── parser.py # Main parsing script
└── output/ # JSON results per command



## 📄 `commands_map.json`
This file provides a **mapping between raw log filenames and TextFSM command templates**.

- **Key** → The canonical command name expected by `ntc-templates`  
- **Value** → A list of **filename patterns** that match local log files  

Example:
```json
{
  "show ip route": [
    "show ip route*",
    "sh ip route*"
  ],
  "show interface": [
    "show interface*",
    "sh int*",
    "show int*"
  ]
} 
```
When parsing:

Show ip route_clean_part9.log → matched to show ip route → loads cisco_ios_show_ip_route.textfsm
sh int Catalyst_clean_part2.log → matched to show interface → loads cisco_ios_show_interface.textfsm

This mapping normalizes inconsistent filenames so the correct template is always used.



## 🚀 Usage

python parser.py -i <input_folder> -o <output_folder>
-i → folder with raw .log files (can contain subfolders)
-o → destination folder for JSON output

## 📌 Example
```
logs/
├── Router1/
│   └── Show ip route_clean_part1.log
├── SwitchA/
│   └── sh int status_clean_part3.log
└── Firewall/
    └── show vlan_clean_part4.log

Command
python parser.py -i ./logs -o ./results

results/
├── show_ip_route_output.json
├── show_interface_output.json
└── show_vlan_output.json
```

🛠 Example Record
``` json
{
  "NETWORK": "192.168.1.0",
  "MASK": "24",
  "DISTANCE": "110",
  "METRIC": "20",
  "NEXTHOP": "10.0.0.1",
  "INTERFACE": "GigabitEthernet0/1",
  "raw": "192.168.1.0 24 110 20 10.0.0.1 GigabitEthernet0/1",
  "source_file": "Router1/Show ip route_clean_part1.log",
  "device_name": "Router1",
  "device_ip": "1.1.1.1",
  "timestamp": "2025-09-18 10:45"
}
``` 

## ✅ Notes
Currently configured for Cisco IOS, but can be extended to other vendors by changing PLATFORM and adding mappings.

If no template is found for a command, the file is skipped.

