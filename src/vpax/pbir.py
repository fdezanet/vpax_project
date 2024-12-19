import json
from pathlib import Path

import pandas as pd


class PageParserError(Exception):
    """Custom exception for page parsing errors."""

    pass


class PageParser:
    def __init__(self, pages_directory: Path):
        """
        Initialize the parser with the path to the 'pages' directory.

        :param pages_directory: A Path object pointing to the directory containing page subfolders.
        """
        self.pages_directory = pages_directory
        self.pages_order = self.get_pages_order()

    def load_pages(self):
        """
        Load and parse all page.json files within the subfolders of the pages directory.

        :return: A list of dictionaries, each containing 'name' and 'displayName'.
        """
        if not self.pages_directory.is_dir():
            raise PageParserError(
                f"The specified pages directory does not exist or is not a directory: {self.pages_directory}"
            )

        pages_data = []

        # Iterate through each subdirectory in the pages directory
        for sub_dir in self.pages_directory.iterdir():
            if sub_dir.is_dir():
                page_json_path = sub_dir / "page.json"
                if page_json_path.is_file():
                    try:
                        with page_json_path.open("r", encoding="utf-8") as f:
                            page_content = json.load(f)
                    except json.JSONDecodeError as e:
                        raise PageParserError(
                            f"JSON decoding error in {page_json_path}: {e}"
                        ) from e
                    except FileNotFoundError:
                        raise PageParserError(
                            f"page.json file not found in directory: {sub_dir}"
                        )

                    name = page_content.get("name")
                    display_name = page_content.get("displayName")

                    if name is None or display_name is None:
                        raise PageParserError(
                            f"page.json in {sub_dir} is missing 'name' or 'displayName' fields."
                        )

                    pages_data.append({"name": name, "displayName": display_name})

        return pages_data

    def load_pages_visuals(self):
        """
        Recursively load and parse all visuals from each page subdirectory.

        The structure is expected to be:
        pages_directory/
          page1/
            page.json
            visual1/
              visual.json
            visual2/
              visual.json
          page2/
            page.json
            ...

        Returns a list of dictionaries, each with:
         - pageName
         - pageDisplayName
         - visualName
         - x
         - y
         - height
         - visualType
        """
        if not self.pages_directory.is_dir():
            raise PageParserError(
                f"The specified pages directory does not exist or is not a directory: {self.pages_directory}"
            )

        visuals_data = []

        # Iterate over each page directory
        for page_dir in self.pages_directory.iterdir():
            if page_dir.is_dir():
                page_json_path = page_dir / "page.json"
                if not page_json_path.is_file():
                    continue  # Not a valid page directory, skip

                with page_json_path.open("r", encoding="utf-8") as f:
                    page_content = json.load(f)

                page_name = page_content.get("name")
                page_display_name = page_content.get("displayName")

                # get page order info from the pages df
                page_order = self.pages_order.loc[
                    self.pages_order["name"] == page_name, "order"
                ].values[0]

                if page_name is None or page_display_name is None:
                    raise PageParserError(
                        f"page.json in {page_dir} is missing 'name' or 'displayName' fields."
                    )

                # Now look for visuals inside this page directory
                # A visual is identified by a directory containing a visual.json
                page_dir = Path(pages_dir) / page_name / "visuals"
                for visual_dir in page_dir.iterdir():
                    if visual_dir.is_dir():
                        visual_json_path = visual_dir / "visual.json"
                        if visual_json_path.is_file():
                            with visual_json_path.open("r", encoding="utf-8") as vf:
                                visual_content = json.load(vf)

                            visual_name = visual_content.get("name")
                            position = visual_content.get("position", {})
                            x = position.get("x")
                            y = position.get("y")
                            height = position.get("height")

                            visual_data = visual_content.get("visual", {})
                            visual_type = visual_data.get("visualType")

                            #             # Validate required fields
                            #             if (
                            #                 visual_name is None
                            #                 or x is None
                            #                 or y is None
                            #                 or height is None
                            #                 or visual_type is None
                            #             ):
                            #                 raise PageParserError(
                            #                     f"visual.json in {visual_dir} is missing required fields (name/position/visualType)."
                            #                 )

                            visuals_data.append(
                                {
                                    "pageName": page_name,
                                    "pageDisplayName": page_display_name,
                                    "pageOrder": page_order,
                                    "visualName": visual_name,
                                    "x": x,
                                    "y": y,
                                    "height": height,
                                    "visualType": visual_type,
                                }
                            )

        visuals_data = pd.DataFrame(visuals_data)

        return visuals_data

    def get_pages_order(self):
        """
        Reads the pageOrder from pages.json and returns a list of page names in order.
        """
        main_pages_file = self.pages_directory / "pages.json"
        if not main_pages_file.is_file():
            raise PageParserError(
                f"pages.json file not found in the pages directory: {self.pages_directory}"
            )

        with main_pages_file.open("r", encoding="utf-8") as f:
            main_pages_content = json.load(f)

        page_order = main_pages_content.get("pageOrder")
        if page_order is None:
            raise PageParserError(
                f"pages.json in {self.pages_directory} does not contain 'pageOrder'."
            )

        # Convert pages_data to a DataFrame
        df = pd.DataFrame(page_order, columns=["name"])

        # Create a mapping from page name to its order (index in page_order)
        order_map = {name: idx for idx, name in enumerate(page_order)}

        # Add an 'order' column based on this mapping
        df["order"] = df["name"].map(order_map)

        # Sort df by the 'order' column
        df.sort_values("order", inplace=True)
        # Reset the index
        df.reset_index(drop=True, inplace=True)

        return df

    def merge_page_order(self, pages_data):
        """
        Reads the pageOrder from pages.json and returns a pandas DataFrame
        containing the name of the page and the corresponding order.
        """
        main_pages_file = self.pages_directory / "pages.json"
        if not main_pages_file.is_file():
            raise PageParserError(
                f"pages.json file not found in the pages directory: {self.pages_directory}"
            )

        with main_pages_file.open("r", encoding="utf-8") as f:
            main_pages_content = json.load(f)

        page_order = main_pages_content.get("pageOrder")
        if page_order is None:
            raise PageParserError(
                f"pages.json in {self.pages_directory} does not contain 'pageOrder'."
            )

        # Convert pages_data to a DataFrame
        df = pd.DataFrame(pages_data)

        # Create a mapping from page name to its order (index in page_order)
        order_map = {name: idx for idx, name in enumerate(page_order)}

        # Add an 'order' column based on this mapping
        df["order"] = df["name"].map(order_map)

        # Sort df by the 'order' column
        df.sort_values("order", inplace=True)
        # Reset the index
        df.reset_index(drop=True, inplace=True)

        # Return only the 'name' and 'order' columns as requested
        return df[["order", "displayName", "name"]]


# Example usage:
if __name__ == "__main__":
    # Example: path to the pages directory within the report structure
    pages_dir = r"xxx.Report\definition\pages"
    path_to_onedrive = Path(r"E:\docs_cloud\OneDrive - Universite de Liege")
    path_to_powerbi_report = (
        path_to_onedrive
        / "_POWERBI"
        / "tdb_internationalisation_project"
        / "report"
        / "DEV"
        / "TDB Internationalisation v8.1"
        / "TDB Internationalisation v08-01.Report"
        / "definition"
        / "pages"
    )

    pages_dir = path_to_powerbi_report
    parser = PageParser(pages_dir)
    # page_order = parser.get_pages_order()
    visuals = parser.load_pages_visuals()
    output = (
        path_to_onedrive
        / "_POWERBI/tdb_internationalisation_project/dm/pbir"
        / "visuals.csv"
    )
    # check path exists
    print(f"Output exists : {output.parent.exists()}")
    print(output)

    visuals.to_csv(output, index=False)
    print(visuals)
    # all_pages = parser.load_pages()
    # ordered_pages = parser.merge_page_order(all_pages)

    # for page in ordered_pages:
    #     print(f"Page: {page['name']} - Display Name: {page['displayName']}")
