import pandas as pd
import psycopg2
from geocode import run_geocoding
from match import match
from tools import read_csv_from_gcs


# Connection BV
host = "localhost"
user = "meilleursagents"
db_name = "meilleursagents_prod"
port = "3333"
password_bv = "****"
uri_bv = f"postgresql://{user}@{host}:{port}/{db_name}"

conn_bv = psycopg2.connect(uri_bv, password=password_bv)


def decode_geo(subregion_cog: int = 75, uri: str = conn_bv):

    sql = f"""
    SELECT
        id,
        cog
    FROM geo.geo_place2
    WHERE
        cog = '{subregion_cog}'
        AND type = 30
        AND enabled = True
        AND active = True
    """

    return pd.read_sql(sql, uri).id.iloc[0]


def get_observation_bv(
    subregion_id: int = 114, date_min: str = "2024-01-01", uri: str = conn_bv
):
    sql = """
    SELECT
        past_sales.id,
        past_sales.address_id,
        address.street_id,
        address.subregion_id,
        past_sales.area,
        past_sales.floor,
        past_sales.energy_consumption_classification,
        past_sales.sale_agreement_date,
        past_sales.type
    FROM public.biz_past_sale AS past_sales
    LEFT JOIN geo.geo_address2 address ON (
        past_sales.address_id = address.id
        AND address.enabled = True
    )
    WHERE
        address.subregion_id = %(subregion_id)s
        AND past_sales.sale_agreement_date::DATE >= %(date_min)s
        AND past_sales.sale_agreement_date::DATE < '2025-05-01'
    """

    table = pd.read_sql(
        sql,
        uri,
        params={"subregion_id": subregion_id, "date_min": date_min},
    ).sort_values(by=["sale_agreement_date"], ascending=False)

    table["item_type"] = table["type"].map({1: "APARTMENT", 2: "HOUSE"})

    return table.dropna(subset=["item_type"])


def sherlock_homes(
    subregion_cog: int = 75, date_min: str = "2024-01-01", uri: str = conn_bv
):
    # Run geocoding
    master_table, failed_addresses = run_geocoding(
        dataset=False,
        start_date="2021-07-01",
        end_date="2025-05-01",
        api_url="https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines",
        query_field="date_reception_dpe",
        query_geo=subregion_cog,
    )

    # Read data
    master_table = read_csv_from_gcs(
        bucket_name="ma-data-dev",
        file_name=f"ADEME/DPE/ADEME_GEOCODED_SUBREGION_CODE_{subregion_cog}",
    )
    master_table["area"] = master_table.surface_habitable_logement.apply(
        lambda x: round(x, 2)
    )

    # Collect past sales
    geo_id = decode_geo(subregion_cog=subregion_cog, uri=uri_bv)
    sales = get_observation_bv(subregion_id=geo_id, date_min=date_min, uri=uri_bv)

    # Run matching
    master, historic, distribution, statistics = match(
        df=sales, searcher_df=master_table, saved=True
    )

    return master, historic, distribution, statistics
