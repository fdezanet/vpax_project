"""
VPAX Extractor Tool

This module provides functionality to extract contents from VPAX files, particularly
focusing on DAX measures stored within them. The extracted measures are converted to
a pandas DataFrame and exported to a CSV file for further analysis. Additionally,
the module sets up logging to track the extraction and conversion process, and the
log files are stored in the same directory as the processed VPAX files.

Functions
---------
- setup_logging(vpax_file: Path) -> None:
    Configures logging for the application, placing log files alongside VPAX files.

- extract_vpax(vpax_file: Path) -> None:
    Extracts the contents of a VPAX file to a specific output directory.

- extract_dax_measures(vpax_file: Path, replace: bool) -> None:
    Extracts DAX measures from the extracted VPAX JSON file and exports them to a CSV.

- run(main_path: Path, replace: bool) -> None:
    Main function that processes all VPAX files in the specified folder, extracting
    DAX measures and logging the process.
"""

import json
import os
import zipfile
from pathlib import Path

import pandas as pd
import typer
from loguru import logger

app = typer.Typer()
output_dir = "extracted"


def setup_logging(vpax_file: Path) -> None:
    """
    Sets up logging configuration for the application. The log file will be placed
    in the same directory as the VPAX file.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file, used to determine where the log file will be saved.
    """
    fmt_info = "{time:YYYY-MM-DD HH:mm:ss} | {name} | {level} | {message}"
    log_file = Path(vpax_file).parent / Path(vpax_file).stem / "vpax.log"

    log_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    logger.add(log_file, format=fmt_info, level="INFO")


def extract_vpax(vpax_file: Path) -> None:
    """
    Extract the contents of a VPAX file to a specific directory.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    """
    path_to_output = Path(vpax_file).parent / Path(vpax_file).stem / output_dir
    logger.info(f"START - Extracting VPAX file: {vpax_file} to {path_to_output}")

    with zipfile.ZipFile(vpax_file, "r") as zip_ref:
        zip_ref.extractall(path_to_output)
        logger.info(f"Extracted VPAX contents to {path_to_output}")

    # Optionally read and process the extracted JSON files if needed
    for root, dirs, files in os.walk(path_to_output):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                logger.info(f"Reading JSON file: {file_path}")
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)


def extract_dax_measures(vpax_file: Path, replace: bool) -> None:
    """
    Extracts DAX measures from a VPAX JSON file and exports the results to CSV.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    replace : bool
        Whether to replace the existing extracted files or not.
    """
    logger.info("START - Extracting DAX measures from VPAX source")

    # Ensure the VPAX extraction has been done
    path_to_json = (
        Path(vpax_file).parent / Path(vpax_file).stem / output_dir / "DaxVpaView.json"
    )

    if replace:
        logger.info("Replace extracted files from vpax")
        extract_vpax(vpax_file)

    elif not path_to_json.exists():
        logger.info(f"{path_to_json} not found. VPAX extraction will be initiated.")
        extract_vpax(vpax_file)

    else:
        logger.info(
            f"VPAX extraction already completed, JSON file found: {path_to_json}"
        )

    # Proceed to extract DAX measures
    try:
        # Read the JSON file
        with open(path_to_json, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        logger.info(f"Successfully read the JSON file: {path_to_json}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {path_to_json}")
        raise e
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file: {path_to_json}")
        raise e

    try:
        # Convert to DataFrame
        df = pd.DataFrame(data["Measures"])
        logger.info(
            f"Successfully converted measures to DataFrame with {df.shape[0]} rows."
        )
    except KeyError as e:
        logger.error(f"'Measures' key not found in the JSON file: {path_to_json}")
        raise e

    # Export to CSV
    output_file = (
        Path(vpax_file).parent
        / Path(vpax_file).stem
        / f"{Path(vpax_file).stem} - DAX.csv"
    )
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)
        logger.info(f"Successfully exported measures to CSV: {output_file}")
    except Exception as e:
        logger.error(f"Error exporting measures to CSV: {output_file}")
        raise e

    logger.info("END - Successfully extracted and saved DAX measures.")


@app.command()
def main(
    main_path: Path = typer.Argument(None, help="The path containing the VPAX files."),
    replace: bool = typer.Option(True, help="Replace the existing files."),
) -> None:
    """
    Main function to find and process all VPAX files in the project folder.
    For each VPAX file found, it extracts DAX measures and saves them.

    Parameters
    ----------
    main_path : Path
        The path to the directory containing the VPAX files.
    replace : bool
        Whether to replace the existing extracted files or not.
    """
    logger.info("LAUNCH PROCESS")

    # Define the path to analyze
    if main_path is None:
        main_path = Path.cwd()

    # Check if the project directory exists
    if not main_path.exists():
        logger.info(f"Project directory not found: {main_path}")
        exit()

    # Find all VPAX files in the project directory
    vpax_files = list(main_path.glob("*.vpax"))

    if not vpax_files:
        logger.info(f"No VPAX files found in the directory: {main_path}")
        exit()

    for path_to_vpax in vpax_files:
        logger.info(f"Processing VPAX file: {path_to_vpax}")

        # Setup logging for each VPAX file
        setup_logging(path_to_vpax)

        extract_dax_measures(path_to_vpax, replace)

    logger.info("All VPAX files processed.")


if __name__ == "__main__":
    app()
