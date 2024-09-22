# VPAX Extractor Tool

The VPAX Extractor Tool is a Python-based utility designed to automate the extraction of DAX measures from VPAX files and convert them into CSV format for easy analysis. This tool simplifies the process of extracting VPAX contents, reading JSON files inside the archive, and saving extracted measures in structured CSV files. Each extraction process is logged, providing an audit trail stored alongside the processed VPAX files.

## Features
- Automatically extracts and processes VPAX files.
- Reads DAX measures from JSON files and exports them to CSV format.
- Generates a log file for each VPAX file in the same directory as the file.
- Can automatically watch a folder for new or modified VPAX files, triggering the extraction process.
- Customizable command-line interface (CLI) with options for replacing files, watching directories, and more.

## Installation

Before running the VPAX Extractor Tool, make sure you have Python installed. To install the package and its dependencies, use the following command, which leverages the `pyproject.toml` file:

```bash
pip install .
```

This command will install the VPAX Extractor Tool and all required dependencies automatically.

## How to Use

### 1. Process a Folder of VPAX Files

To process all VPAX files in a specific folder, use the following command:

```bash
vpax process-folder <path_to_vpax_files> --replace
```

If no path is provided, the script will default to the current working directory.
The `--replace` option controls whether to re-extract VPAX files that have already been processed.

### 2. Watch a Folder for New or Modified VPAX Files

You can configure the tool to watch a folder for new or modified .vpax files, automatically triggering the extraction process when changes are detected:

```bash
vpax watch-folder <path_to_vpax_files> --replace
```

The script will continue running, monitoring the folder for any new or modified VPAX files.
The --replace option works the same as in the process-folder command.

## Command-Line Interface (CLI) Options

The VPAX Extractor Tool provides a user-friendly command-line interface using Typer to customize how you process VPAX files.

1. main_path (Positional Argument)

    Description: The path to the directory containing the VPAX files.
    Usage: This argument is optional. If not provided, the script defaults to the current working directory.
    Example:

    ```bash
    vpax process-folder "C:/Users/username/Documents/VPAX_Files"
    ```

2. --replace (Boolean Option)

    Description: Determines whether to re-extract files even if they have already been processed.
    Type: Boolean (True or False)
    Default: True
    Usage: Add --no-replace if you want to skip extracting files that have already been processed.
    Example:

    ```bash
    python script.py process-folder "C:/Users/username/Documents/VPAX_Files" --no-replace
    ```

3. folder_to_watch (Positional Argument for watch-folder)

    Description: The path to the folder you want to monitor for new or modified VPAX files.
    Usage: This argument is optional. If not provided, the current working directory will be used.
    Example:

    ```bash

    python script.py watch-folder "C:/Users/username/Documents/VPAX_Files"
    ```

## Logging

A separate log file is generated for each VPAX file processed, saved in the same directory as the file.
The log file records information such as when the extraction process started, any errors encountered, and when the extraction completed successfully.

## License

This project is licensed under the MIT License. Feel free to modify and use the tool as per your needs.