import json
import os
import zipfile
from pathlib import Path

import pandas as pd
import typer
from loguru import logger

app = typer.Typer()
output_dir = "extracted"


def setup_logging(log_file: Path) -> None:
    """
    Sets up logging configuration for the application.

    Parameters
    ----------
    log_file : Path
        The path to the log file where log messages will be saved.
    """

    fmt_info = "{time:YYYY-MM-DD HH:mm:ss} | {name} | {level} | {message}"
    log_file = Path(log_file)

    logger.add(log_file, format=fmt_info, level="INFO")


# Initialize logging
setup_logging(Path("./logs/vpax.log"))


def extract_vpax(vpax_file: Path) -> None:
    """
    Extract the VPAX file and read the content, particularly the JSON files.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    output_dir : Path
        The directory where the contents of the VPAX file will be extracted.
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
    Extracts DAX measures from the extracted VPAX JSON file, converts them to a DataFrame,
    and exports the result to a CSV file. If the VPAX extraction has not been performed yet,
    it triggers the VPAX extraction process first.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    output_dir : Path
        The directory where the VPAX contents should be extracted.
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
def run(
    main_path: Path = typer.Argument(None, help="The path containing the vpax files."),
    replace: bool = typer.Option(True, help="Replace the existing files."),
) -> None:
    """
    Main function to find and process all VPAX files in the project folder.
    For each VPAX file found, it extracts DAX measures and saves them.
    """
    logger.info("LAUNCH PROCESS")

    # Define tha path to analyze
    if main_path is None:
        main_path = Path.cwd()
        # main_path = Path("./data/TDB Stat de consultations")

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

        extract_dax_measures(path_to_vpax, replace)

    logger.info("All VPAX files processed.")


if __name__ == "__main__":
    app()
