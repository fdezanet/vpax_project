import json
import os
import time
import zipfile
from pathlib import Path

import pandas as pd
import typer
from loguru import logger
from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

app = typer.Typer()
output_dir = "extracted"


class VPAXEventHandler(FileSystemEventHandler):
    """
    Event handler for detecting new or modified VPAX files.
    When a .vpax file is created or modified, it triggers the extraction process.

    Parameters
    ----------
    folder_to_watch : Path
        The folder being watched for changes.
    replace : bool
        Flag indicating whether to replace existing extracted files.
    """

    def __init__(self, folder_to_watch: Path, replace: bool):
        self.folder_to_watch = folder_to_watch
        self.replace = replace

    def on_modified(self, event):
        """
        Handler for the modified event. If the modified file is a VPAX file,
        triggers the extraction process.

        Parameters
        ----------
        event : watchdog.events.FileModifiedEvent
            The file system event triggered by file modification.
        """
        if isinstance(event, FileModifiedEvent) and event.src_path.endswith(".vpax"):
            vpax_file = Path(event.src_path)
            logger.info(f"Modified VPAX file detected: {vpax_file}")
            process_vpax_file(vpax_file, self.replace)

    def on_created(self, event):
        """
        Handler for the created event. If the created file is a VPAX file,
        triggers the extraction process.

        Parameters
        ----------
        event : watchdog.events.FileCreatedEvent
            The file system event triggered by file creation.
        """
        if isinstance(event, FileCreatedEvent) and event.src_path.endswith(".vpax"):
            vpax_file = Path(event.src_path)
            logger.info(f"New VPAX file detected: {vpax_file}")
            process_vpax_file(vpax_file, self.replace)


def setup_logging(vpax_file: Path) -> None:
    """
    Configures logging for the application, placing log files alongside the VPAX files.

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
        The path to the VPAX file that needs to be extracted.
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


def extract_infos(vpax_file: Path, replace: bool, infos: list = None) -> None:
    """
    Extracts DAX measures from a VPAX JSON file and exports them to a CSV.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    replace : bool
        Whether to replace the existing extracted files.
    """
    logger.info("START - Extracting DAX measures from VPAX source")

    # Check infos to extract
    if infos is None:
        infos = ["Measures", "Tables", "Columns", "Relationships"]
        logger.info(f"Default infos to extract: {infos}")

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

    for info in infos:
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data[info])
            logger.info(
                f"Successfully converted {info} to DataFrame with {df.shape[0]} rows."
            )
        except KeyError as e:
            logger.error(f"'{info}' key not found in the JSON file: {path_to_json}")
            raise e

        # Export to CSV
        output_file = (
            Path(vpax_file).parent
            / Path(vpax_file).stem
            / f"{Path(vpax_file).stem} - {info}.csv"
        )
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_file, index=False)
            logger.info(f"Successfully exported {info} to CSV: {output_file}")
        except Exception as e:
            logger.error(f"Error exporting {info} to CSV: {output_file}")
            raise e

        logger.info("END - Successfully extracted and saved {info}.")

    logger.info("END - Extracting informations from VPAX source")


def process_vpax_file(vpax_file: Path, replace: bool) -> None:
    """
    Process the VPAX file by setting up logging, extracting data, and saving DAX measures.

    Parameters
    ----------
    vpax_file : Path
        The path to the VPAX file.
    replace : bool
        Whether to replace the existing extracted files or not.
    """
    setup_logging(vpax_file)
    extract_infos(vpax_file, replace)


@app.command()
def process_folder(
    main_path: Path = typer.Argument(None, help="The path containing the VPAX files."),
    replace: bool = typer.Option(True, help="Replace the existing files."),
) -> None:
    """
    Main function to find and process all VPAX files in the specified folder.
    For each VPAX file found, it extracts DAX measures and saves them to CSV.

    Parameters
    ----------
    main_path : Path
        The path to the directory containing the VPAX files. If not provided, defaults
        to the current working directory.
    replace : bool
        Whether to replace the existing extracted files. Defaults to True.
    """
    logger.info("LAUNCH PROCESS")

    # Define the path to analyze
    if main_path is None:
        main_path = Path.cwd()

    # Check if the project directory exists
    if not main_path.exists():
        logger.info(f"Project directory not found: {main_path}")
        raise typer.Exit(code=1)

    # Find all VPAX files in the project directory
    vpax_files = list(main_path.glob("*.vpax"))

    if not vpax_files:
        logger.info(f"No VPAX files found in the directory: {main_path}")
        raise typer.Exit(code=1)

    for path_to_vpax in vpax_files:
        logger.info(f"Processing VPAX file: {path_to_vpax}")

        # Setup logging for each VPAX file
        setup_logging(path_to_vpax)

        extract_infos(path_to_vpax, replace)

    logger.info("All VPAX files processed.")


@app.command()
def watch_folder(
    folder_to_watch: Path = typer.Argument(
        None, help="The path containing the VPAX files."
    ),
    replace: bool = typer.Option(True, help="Replace the existing files."),
) -> None:
    """
    Watches the specified folder for changes and triggers VPAX extraction when new or
    modified files are detected.

    If no folder is provided, the current working directory will be used by default.

    Parameters
    ----------
    folder_to_watch : Path, optional
        The path to the directory containing the VPAX files. Defaults to the current
        working directory if not provided.
    replace : bool, optional
        Whether to replace the existing extracted files or not. Defaults to True.
    """
    logger.info("LAUNCH PROCESS")

    # Define the folder to watch
    if folder_to_watch is None:
        folder_to_watch = Path.cwd()

    # Check if the project directory exists
    if not folder_to_watch.exists():
        logger.error(f"Project directory not found: {folder_to_watch}")
        raise typer.Exit(code=1)

    logger.info(f"Watching folder: {folder_to_watch}")

    # Setup the event handler and observer
    event_handler = VPAXEventHandler(folder_to_watch, replace)
    observer = Observer()
    observer.schedule(event_handler, path=str(folder_to_watch), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)  # Sleep to avoid excessive CPU usage
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()


if __name__ == "__main__":
    app()
