#!/usr/bin/env python3
"""
Mailbox Size Report Script - Version V8.1
Description: Fetches and displays mailbox sizes for all cPanel accounts using WHM API remotely.
"""

import sys
import subprocess
import importlib
import json
import argparse
import pandas as pd
import time
import requests
import socket
from tabulate import tabulate
from urllib3.exceptions import InsecureRequestWarning

# Remote WHM API Details
REMOTE_HOST = "domain.com"
API_TOKEN = "WHM_TOKEN"
WHM_API_URL = f"https://{REMOTE_HOST}:2087/json-api"

# Required modules list
REQUIRED_MODULES = ["requests", "pandas", "tabulate"]

# Function to check and install missing modules
def check_and_install_modules():
    missing_modules = []

    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("\n\033[1;31mMissing required modules:\033[0m", ", ".join(missing_modules))
        for module in missing_modules:
            while True:
                choice = input(f"Would you like to install '\033[1;32m{module}\033[0m'? (y/n): ").strip().lower()
                if choice == "y":
                    print(f"\nInstalling {module}...\n")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                    break
                elif choice == "n":
                    print("\n\033[1;31mRequired module missing. Aborting.\033[0m")
                    sys.exit(1)
                else:
                    print("\033[1;31mInvalid input. Please enter 'y' or 'n'.\033[0m")

        for module in missing_modules:
            importlib.import_module(module)

# Run module check before anything else
check_and_install_modules()

# Function to run WHM API calls remotely
def run_whmapi(api_function, params=None, verify_ssl=True, debug=False):
    headers = {
        "Authorization": f"whm root:{API_TOKEN}"
    }
    
    url = f"{WHM_API_URL}/{api_function}"
    response = requests.get(url, headers=headers, params=params, verify=verify_ssl)

    if debug:
        print(f"\n\033[1;33m[DEBUG] API Request: {url}\033[0m")
        print(f"\033[1;33m[DEBUG] Response: {response.text}\033[0m")

    if response.status_code != 200:
        print(f"\033[1;31mError: WHM API request failed ({response.status_code})\033[0m")
        sys.exit(1)

    return response.json()

# Function to get all cPanel users remotely
def get_cpanel_users(verify_ssl=True, debug=False):
    params = {"api.version": "1"}
    data = run_whmapi("listaccts", params=params, verify_ssl=verify_ssl, debug=debug)

    if not data or "data" not in data or "acct" not in data["data"]:
        print("\033[1;31mError: No cPanel users found.\033[0m")
        sys.exit(1)
    
    return [user["user"] for user in data["data"]["acct"]]

# Function to fetch mailboxes for a user using WHM API
def get_mailboxes(user, verify_ssl=True, debug=False):
    params = {
        "api.version": "1",
        "cpanel_jsonapi_user": user,
        "cpanel_jsonapi_module": "Email",
        "cpanel_jsonapi_func": "list_pops_with_disk",
        "cpanel_jsonapi_apiversion": "3"
    }
    data = run_whmapi("cpanel", params=params, verify_ssl=verify_ssl, debug=debug)

    if not data or "result" not in data or "data" not in data["result"]:
        return []

    return data["result"]["data"]

# Function to convert bytes to a human-readable format
def convert_to_human(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes >= 1024**4:
        return f"{size_bytes / (1024**4):.2f} TB"
    elif size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"

# Function to collect all mailboxes
def collect_mailboxes(users, hide_empty=False, verify_ssl=True, debug=False):
    mailbox_data = []
    for user in users:
        mailboxes = get_mailboxes(user, verify_ssl, debug)
        if not mailboxes:
            continue

        for mailbox in mailboxes:
            email = mailbox["email"]
            domain = mailbox["domain"]
            size_bytes = int(float(mailbox.get("_diskused", 0)))

            if hide_empty and size_bytes == 0:
                continue  # Skip empty mailboxes if --hide-empty is used

            size_human = convert_to_human(size_bytes)
            mailbox_data.append([user, email, domain, size_bytes, size_human])

    return mailbox_data

# Main script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch mailbox sizes from WHM remotely (Version V8.1)")
    parser.add_argument("-t", type=int, help="Show only the top X largest mailboxes")
    parser.add_argument("-u", type=str, help="Filter results for specific cPanel users (comma-separated)")
    parser.add_argument("-o", type=str, help="Output results as a CSV file")
    parser.add_argument("--hide-empty", action="store_true", help="Hide mailboxes with zero storage")

    args = parser.parse_args()
    start_time = time.time()
    
    verify_ssl = True  # Ensure SSL verification is handled correctly
    users = get_cpanel_users(verify_ssl=verify_ssl)

    if args.u:
        users = args.u.split(",")

    mailbox_data = collect_mailboxes(users, hide_empty=args.hide_empty, verify_ssl=verify_ssl)

    df = pd.DataFrame(mailbox_data, columns=["cPanel_User", "Email", "Domain", "Size_Bytes", "Size_Human"])
    df["Size_Bytes"] = df["Size_Bytes"].astype(int)

    if args.t:
        df = df.sort_values(by="Size_Bytes", ascending=False).head(args.t)
        print(f"\n\033[1;34mTop {args.t} Largest Mailboxes Across All Accounts\033[0m")
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
    else:
        print("\n\033[1;34mMailbox Sizes for All cPanel Users (Sorted by Account and Domain)\033[0m")

        account_totals = df.groupby("cPanel_User")["Size_Bytes"].sum().reset_index()
        account_totals = account_totals.sort_values(by="Size_Bytes", ascending=False)

        for _, row in account_totals.iterrows():
            user = row["cPanel_User"]
            user_df = df[df["cPanel_User"] == user]
            account_total = convert_to_human(user_df["Size_Bytes"].sum())

            print(f"\n\033[1;33m-------- Account: {user} (Total: {account_total}) --------\033[0m")
            for domain in user_df["Domain"].unique():
                domain_df = user_df[user_df["Domain"] == domain].sort_values(by="Size_Bytes", ascending=False)
                domain_total = convert_to_human(domain_df["Size_Bytes"].sum())

                print(f"\n\033[1;36m📂 Domain: {domain} (Total: {domain_total})\033[0m")
                print(tabulate(domain_df, headers="keys", tablefmt="grid", showindex=False))

    print(f"\n\033[1;32mExecution Time:\033[0m {round(time.time() - start_time, 2)} seconds")
    print(f"\033[1;32mServer:\033[0m {REMOTE_HOST}")
    print(f"\033[1;32mTotal Mailboxes Processed:\033[0m {len(mailbox_data)}")
