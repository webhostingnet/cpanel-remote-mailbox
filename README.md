# Mailbox Size Report Script (Version V8.1)

## Overview

This script fetches and displays mailbox sizes for all cPanel accounts using the **WHM API** remotely. It provides an organized, sortable report of mailbox usage across multiple domains and users.

The script is useful for **system administrators** managing cPanel accounts who need insights into email storage usage. It can help **identify large mailboxes**, **track storage trends**, and **export data for reporting**.

## Configuration

Before running the script, you **must update** the following variables inside `mailbox.v8.1.remote.py`:

```python
REMOTE_HOST = "domain.com"  # Replace with your WHM/cPanel server hostname
API_TOKEN = "WHM_TOKEN"     # Replace with your WHM API token
```

### How to Obtain Your WHM API Token:

1. Log in to **WHM** as root.
2. Go to **Development → Manage API Tokens**.
3. Click **Generate Token**.
4. Copy the token and replace `API_TOKEN` in the script.

**Note:** Ensure that the API token has permissions to list accounts and email information.

## Features & Benefits

- ✅ **Automates WHM API calls** to fetch mailbox sizes for all cPanel accounts.
- ✅ **Sorts and displays results** grouped by account and domain.
- ✅ **Supports filtering by user** to view specific cPanel accounts.
- ✅ **Option to hide empty mailboxes** for a cleaner output.
- ✅ **Generates CSV reports** for data analysis and auditing.
- ✅ **Displays execution time** and processed mailbox count.

## Output Example

### Sample Terminal Output:

```
Mailbox Sizes for All cPanel Users (Sorted by Account and Domain)

-------- Account: user123 (Total: 5.98 GB) --------

📂 Domain: exampledomain.com (Total: 5.12 GB)

+---------------+--------------------------+-------------------+--------------+--------------+
| cPanel_User   | Email                    | Domain            |   Size_Bytes | Size_Human   |
+===============+==========================+===================+==============+==============+
| user123       | alice@exampledomain.com  | exampledomain.com |   1701232945 | 1.58 GB      |
| user123       | bob@exampledomain.com    | exampledomain.com |   1508722831 | 1.40 GB      |
| user123       | charlie@exampledomain.com| exampledomain.com |   1358027928 | 1.26 GB      |
| user123       | dave@exampledomain.com   | exampledomain.com |   1206915814 | 1.12 GB      |
| user123       | support@exampledomain.com| exampledomain.com |    293242722 | 279.66 MB    |
+---------------+--------------------------+-------------------+--------------+--------------+

Execution Time: 1.56 seconds  
Server: domain.com  
Total Mailboxes Processed: 9
```

## Installation

Ensure you have **Python 3** installed. The script automatically checks for required Python modules and installs them if missing.

## Usage

Run the script from the command line:

```bash
python3 mailbox.v8.1.remote.py
```

### Command-Line Options:

| Option        | Description |
|--------------|-------------|
| `-t X`       | Show only the **top X largest mailboxes** |
| `-u user1,user2` | Filter results for **specific cPanel users** (comma-separated) |
| `-o output.csv` | Export mailbox data to a **CSV file** |
| `--hide-empty` | Hide mailboxes with **zero storage usage** |

### Example Commands:

#### Show only the 5 largest mailboxes:
```bash
python3 mailbox.v8.1.remote.py -t 5
```

#### Filter results for specific users:
```bash
python3 mailbox.v8.1.remote.py -u user123,user456
```

#### Export data to CSV:
```bash
python3 mailbox.v8.1.remote.py -o mailboxes.csv
```

#### Hide empty mailboxes:
```bash
python3 mailbox.v8.1.remote.py --hide-empty
```

## Requirements

- **cPanel/WHM API access** (Admin privileges required)
- **Python 3.x**
- **Modules:** `requests`, `pandas`, `tabulate`

The script automatically installs missing dependencies. If it does't you can use run "pip3 install <module_name>" from the command line

## License

This script is open-source and can be modified as needed.
