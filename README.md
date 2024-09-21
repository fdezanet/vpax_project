# VPAX Extractor Tool

The VPAX Extractor Tool is a Python script that extracts DAX measures from VPAX files and converts them into CSV format for easy analysis. This tool automates the process of extracting VPAX contents, reading JSON files within the archive, and saving extracted measures in a structured CSV file. Logs are created for each VPAX file and stored in the same directory, providing an audit trail of the extraction process.

## Features
- Automatically extracts VPAX files and processes their contents.
- Reads DAX measures from JSON files and exports them to CSV.
- Generates log files for each VPAX file, saved in the same directory as the file.
- Easy to use and customizable with command-line options.

## How to Use
1. Place your VPAX files in a folder.
2. Run the `vpax` command from the folder.
3. The DAX measures will be extracted and saved as CSV files, and logs will be generated in the same folder as the VPAX files.

## Command-Line Interface (CLI) Options (using Typer)

The VPAX Extractor Tool provides a simple command-line interface to customize how you extract and process VPAX files. 

Below are the available options:

1. `main_path` (Positional Argument)
   - **Description**: The path to the directory containing the VPAX files.
   - **Usage**: This argument is optional. If not provided, the script will default to the current working directory.
   - **Example**: vpax "C:/Users/username/Documents/VPAX_Files"

2. `--replace` (Option)
   - **Description**: Indicates whether to replace the existing extracted files. If set to `True`, the script will re-extract VPAX files even if they have already been processed.
   - **Type**: Boolean (`True` or `False`)
   - **Default**: `True`
   - **Example**: `vpax --no-replace`


    This will skip the extraction if the files are already present.