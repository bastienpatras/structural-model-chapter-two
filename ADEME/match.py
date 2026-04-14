import logging
import warnings

import numpy as np
import pandas as pd
from tools import export_to_gcs


warnings.filterwarnings("ignore")


def compute_dpe(a, b):
    """
    Compares two letters and returns the one that comes first in the alphabet.
    Assumes both inputs are single alphabetical characters.
    """
    # Ensure the function operates on individual values, not Series.
    if isinstance(a, str) and isinstance(b, str):
        a = a.lower()
        b = b.lower()
        return b.upper() if a < b else a.upper()
    else:
        # Handle case if a or b are not strings
        return pd.NA  # Or any other value indicating failure to compute


class PropertySearcherDF:
    """
    A class for searching property records (apartments or houses) in a DataFrame
    based on various criteria such as address, floor, area, and DPE (energy efficiency label).

    For apartments:
        - Matches on floor with a soft penalty for floor mismatches (Gaussian scoring).
    For houses:
        - Ignores floor differences.

    Also includes:
        - Area similarity scoring.
        - Date-based scoring (older DPE dates are penalized).
        - Label dispersion scoring based on frequency of energy labels among candidates.
    """

    def __init__(self, dataframe):
        """
        Initializes the searcher by preparing and transforming the DataFrame for use.
        """
        self.df = dataframe.copy()
        self.df["date_reception_dpe"] = pd.to_datetime(
            self.df["date_reception_dpe"], errors="coerce"
        )
        self.df["floor"] = pd.to_numeric(self.df["floor"], errors="coerce")
        self.df["address_id"] = self.df["id_legacy"]
        self.df["street_id"] = self.df["id_legacy"]
        self.df["ademe_floor"] = pd.to_numeric(self.df["floor"], errors="coerce")
        self.df["ademe_area"] = pd.to_numeric(self.df["area"], errors="coerce")
        self.df["complement_adresse_logement"] = self.df["complement_adresse_logement"]
        self.df["ademe_dpe"] = self.df.apply(
            lambda x: compute_dpe(x["etiquette_dpe"], x["etiquette_ges"]), axis=1
        )

    def area_score(self, row_area, query_area, area_threshold=6):
        """
        Computes area similarity score (1.0 = identical, 0.0 = far apart).
        """
        return max(0.0, min(1.0, 1 - abs(row_area - query_area) / area_threshold))

    def date_score(self, dpe_date, publication_date, decay_factor=365):
        """
        Scores based on recency of DPE vs publication date. Penalizes older DPE dates.
        """
        if pd.isna(dpe_date):
            return 0.7  # Mild penalty for missing dates
        days_diff = (publication_date - dpe_date).days
        if days_diff < 0:
            return 0.0  # Future dates are invalid
        return max(0.0, min(1.0, 1 - days_diff / decay_factor))

    def floor_score_gaussian(self, row_floor, query_floor, sigma=1.0):
        """
        Scores floor proximity using a Gaussian function.
        """
        if pd.isna(row_floor) or pd.isna(query_floor):
            return 0.0
        distance = row_floor - query_floor
        score = np.exp(-0.5 * (distance / sigma) ** 2)
        return max(0.0, min(1.0, score))

    def letter_count(self, candidates):
        """
        Counts the frequency distribution of DPE letters in groups: AB, CDE, FG.
        """
        count_abc = (
            round(sum(c in "AB" for c in candidates) / len(candidates), 2)
            if len(candidates) != 0
            else 0
        )
        count_de = (
            round(sum(c in "CDE" for c in candidates) / len(candidates), 2)
            if len(candidates) != 0
            else 0
        )
        count_fg = (
            round(sum(c in "FG" for c in candidates) / len(candidates), 2)
            if len(candidates) != 0
            else 0
        )
        return [count_abc, count_de, count_fg]

    def score_letter_dispersion(self, freq_ab, freq_cde, freq_fg):
        """
        Calculates dispersion score based on the deviation from uniform label distribution.
        """
        score_ab = max(freq_ab - 1 / 3, 0)
        score_cde = max(freq_cde - 1 / 3, 0)
        score_fg = max(freq_fg - 1 / 3, 0)
        return (score_ab + score_cde + score_fg) * 3 / 2

    def score_match(
        self,
        row,
        floor,
        area,
        candidates,
        publication_date=None,
        use_floor=True,
        area_weight=0.5,
        floor_weight=0.1,
        date_weight=0.2,
        dispersion_weight=0.2,
    ):
        """
        Aggregates individual scores (area, floor, date, dispersion) into a single match score.
        """
        area_score = self.area_score(row["area"], area)
        floor_score = (
            self.floor_score_gaussian(row["floor"], floor) if use_floor else 0.0
        )
        date_score = (
            self.date_score(row["date_reception_dpe"], publication_date)
            if publication_date is not None
            else 1.0
        )
        letters = self.letter_count(candidates)
        letter_dispersion_score = self.score_letter_dispersion(*letters)

        total_score = (
            area_score * area_weight
            + floor_score * floor_weight
            + date_score * date_weight
            + letter_dispersion_score * dispersion_weight
        )
        return round(total_score, 3)

    def search(
        self,
        address_id,
        street_id,
        floor,
        area,
        floor_threshold=5,
        area_threshold=3,
        item_type="APARTMENT",
        publication_date=None,
    ):
        """
        Main search method:
        Filters and scores potential property matches based on the specified criteria.

        Parameters:
            - address_id: Address identifier to match.
            - street_id: Fallback identifier for houses.
            - floor: Desired floor (only for apartments).
            - area: Desired living area.
            - floor_threshold: Tolerance in floor matching.
            - area_threshold: Tolerance in area matching.
            - item_type: "APARTMENT" or "HOUSE".
            - publication_date: Reference date to penalize old DPEs.

        Returns:
            - List of matched records with scores.
            - Dictionary of intermediate match stages for debugging or analysis.
        """
        matches = self.df[
            (self.df["address_id"] == address_id)
            & (abs(self.df["area"] - area) <= area_threshold)
        ].copy()

        match_counts = {
            "area_stage": [],
            "street_stage": [],
            "date_stage": [],
            "floor_stage": [],
            "compelement_address": [],
            "scores": [],
        }

        candidates = matches.ademe_dpe.to_list()
        match_counts["area_stage"] += candidates

        if publication_date is not None:
            publication_date = pd.to_datetime(publication_date, errors="coerce")
            matches = matches[
                matches["date_reception_dpe"].isna()
                | (matches["date_reception_dpe"] < publication_date)
            ]
            match_counts["date_stage"] += matches.ademe_dpe.to_list()

        if matches.empty and item_type.upper() == "HOUSE":
            # Fallback to street-level match
            matches = self.df[
                (self.df["street_id"] == street_id)
                & (abs(self.df["area"] - area) <= area_threshold)
            ].copy()
            if publication_date is not None:
                matches = matches[
                    matches["date_reception_dpe"].isna()
                    | (matches["date_reception_dpe"] < publication_date)
                ]
            match_counts["street_stage"] += matches.ademe_dpe.to_list()

        if matches.empty:
            return pd.DataFrame(), match_counts

        if item_type.upper() == "HOUSE":
            # No floor consideration
            matches["match_score"] = matches.apply(
                lambda row: self.score_match(
                    row, floor, area, candidates, publication_date, use_floor=False
                ),
                axis=1,
            )
            matches["match_score"] *= 0.9  # Slight penalty for fallback
            return (
                matches.sort_values("match_score", ascending=False).to_dict(
                    orient="records"
                ),
                match_counts,
            )

        # Handle floor parsing
        matches["floor"] = pd.to_numeric(matches["floor"], errors="coerce")
        try:
            floor = float(floor)
        except Exception:
            floor = np.nan

        valid_matches = (
            matches[
                matches["floor"].isna()
                | (abs(matches["floor"] - floor) <= floor_threshold)
            ].copy()
            if len(matches) > 1
            else matches.copy()
        )

        if valid_matches.empty:
            return pd.DataFrame(), match_counts

        valid_matches["match_score"] = valid_matches.apply(
            lambda row: self.score_match(
                row, floor, area, candidates, publication_date, use_floor=True
            ),
            axis=1,
        )

        match_counts["floor_stage"] += valid_matches.ademe_dpe.to_list()
        match_counts[
            "compelement_address"
        ] += valid_matches.complement_adresse_logement.to_list()
        match_counts["scores"] += valid_matches.match_score.to_list()

        return (
            valid_matches.sort_values("match_score", ascending=False).to_dict(
                orient="records"
            ),
            match_counts,
        )


def create_size_report_df(df, list_columns):
    size_data = {
        col: df[col].apply(lambda x: len(x) if isinstance(x, list) else x)
        for col in list_columns
    }
    return pd.DataFrame(size_data, index=df.index)


def true_one(a, b):
    return 0 if a == b == 1 else b


def distribution_checks(df, list_columns):
    data = create_size_report_df(df, list_columns)
    data["area"] = data["area_stage"]
    data["date"] = data.apply(
        lambda x: true_one(x["date_stage"], x["area_stage"]), axis=1
    )
    data["floor"] = data.apply(
        lambda x: true_one(x["floor_stage"], x["date_stage"]), axis=1
    )
    data["street"] = data.apply(
        lambda x: true_one(x["street_stage"], x["date_stage"]), axis=1
    )
    data = data[data.area != 0]
    return (
        data[["area", "date", "floor", "street", "item_type"]]
        .melt(
            id_vars=["item_type"],
            value_vars=["area", "date", "floor", "street"],
            var_name="stages",
        )
        .groupby(["stages", "item_type"])
        .describe(percentiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    )


def match(df, searcher_df, saved=True):
    searcher = PropertySearcherDF(searcher_df)

    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Pre-allocate lists for storing results
    master_rows = []
    historic_rows = []
    distribution = []

    # Loop over rows and collect data
    for idx, (
        sale_id,
        address_id,
        street_id,
        floor,
        area,
        publication_date,
        disclosed_dpe,
        item_type,
    ) in enumerate(
        zip(
            df["id"],
            df["address_id"],
            df["street_id"],
            df["floor"],
            df["area"],
            df["sale_agreement_date"],
            df["energy_consumption_classification"],
            df["item_type"],
        )
    ):
        # Search for matching energy data based on property features
        results, distribution_dict = searcher.search(
            address_id=address_id,
            street_id=street_id,
            floor=floor,
            area=area,
            publication_date=publication_date,
            item_type=item_type,
        )

        # Ensure results is a DataFrame, if it is a list
        if isinstance(results, list):
            results = pd.DataFrame(results)

        # Handle case where no results are found
        if results.empty:
            master_rows.append(
                {
                    "sale_id": sale_id,
                    "street_id": street_id,
                    "address_id": address_id,
                    "area": area,
                    "sale_agreement_date": publication_date,
                    "disclosed_dpe": disclosed_dpe,
                    "floor": floor,
                    "item_type": item_type,
                    "ademe_dpe": pd.NA,
                }
            )
        else:
            # Results found: Add metadata and compute DPE
            results["sale_id"] = sale_id
            results["street_id"] = street_id
            results["address_id"] = address_id
            results["area"] = area
            results["sale_agreement_date"] = publication_date
            results["disclosed_dpe"] = disclosed_dpe
            results["floor"] = floor
            results["item_type"] = item_type

            # Apply compute_dpe element-wise to the rows
            results["ademe_dpe"] = results.apply(
                lambda row: compute_dpe(row["etiquette_dpe"], row["etiquette_ges"]),
                axis=1,
            )

            # Append the first match and all historic matches
            master_rows.append(
                results.iloc[0].to_dict()
            )  # Ensure it's a dict for consistency
            historic_rows.append(results)

        # Handle distribution data (if any)
        if distribution_dict:
            distribution_data = pd.DataFrame([distribution_dict])
            distribution_data["sale_id"] = sale_id
            distribution_data["floor"] = floor
            distribution_data["item_type"] = item_type
            distribution_data["address_id"] = address_id
            distribution.append(distribution_data)

        # Log every 1000 rows
        if (idx + 1) % 1000 == 0:
            logger.info(f"Processed {idx + 1} rows")

    # Ensure all dictionaries in master_rows have the same structure
    if master_rows:
        # Make sure the dictionary keys are consistent
        columns = master_rows[
            0
        ].keys()  # Use the keys from the first row as column names
        master = pd.DataFrame(master_rows, columns=columns)
    else:
        master = pd.DataFrame()  # If master_rows is empty, create an empty DataFrame

    # Concatenate historic rows
    historic = (
        pd.concat(historic_rows, ignore_index=True) if historic_rows else pd.DataFrame()
    )

    # Concatenate distribution rows
    distribution = (
        pd.concat(distribution, ignore_index=True) if distribution else pd.DataFrame()
    )
    distribution["area_stage"] = distribution["area_stage"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    distribution[["AB", "CDE", "FG"]] = (
        distribution["area_stage"].apply(searcher.letter_count).apply(pd.Series)
    )

    # Export data to GCS
    ## Export
    if saved:
        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/AVM_DATA/{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}"
            f"/SALES_ENRICHED_SUBREGION_CODE_{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}.csv",
            new_df=master.reset_index(drop=True)[
                [
                    "sale_id",
                    "id_aviv",
                    "numero_dpe",
                    "match_score",
                    "ademe_dpe",
                    "etiquette_dpe",
                    "etiquette_ges",
                    "date_visite_diagnostiqueur",
                ]
            ],
        )

        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/AVM_DATA/{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}"
            f"/SALES_ENRICHED_HISTORIC_SUBREGION_CODE_{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}.csv",
            new_df=historic.reset_index(drop=True),
        )

        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/AVM_DATA/{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}"
            f"/SALES_ENRICHED_DISTRIBUTION_SUBREGION_CODE_{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}.csv",
            new_df=distribution.reset_index(drop=True),
        )

        export_to_gcs(
            bucket_name="ma-data-dev",
            blob_name=f"ADEME/AVM_DATA/{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}"
            f"/SALES_ENRICHED_STATISTICS_SUBREGION_CODE_{str(int(master.code_departement_ban.dropna().drop_duplicates().iloc[0]))}.csv",
            new_df=distribution_checks(
                distribution,
                [
                    "area_stage",
                    "date_stage",
                    "floor_stage",
                    "street_stage",
                    "item_type",
                ],
            ),
        )

    return (
        master.reset_index(drop=True),
        historic.reset_index(drop=True),
        distribution.reset_index(drop=True),
        distribution_checks(
            distribution,
            ["area_stage", "date_stage", "floor_stage", "street_stage", "item_type"],
        ),
    )
