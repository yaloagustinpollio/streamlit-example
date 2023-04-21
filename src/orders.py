import pandas as pd
import tempfile

from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime
import os

os.environ["GCLOUD_PROJECT"] = "algo-selling-prod-da6c"
BIGQUERY_CLIENT = bigquery.Client()

def aggregated_order_items_in_buyorder(df):
    df = (
        df.groupby(["user_id", "store_code", "session_id", "order_id", "created_at"])
        .agg(
            {
                "quantity": "sum",
                "item_total_amount": "sum",
                "sku": lambda x: ",".join(x),
            }
        )
        .rename(
            columns={
                "quantity": "total_quantity",
                "item_total_amount": "ticket_size",
                "sku": "sku_list",
            }
        )
    )
    df = df.reset_index()
    return df


def get_order_items(bot_id, storefront_name=None, start_date=None, end_date=None, sku_allowlist=None):
    if end_date is None:
        # ongoing experiment
        end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    storefront_condition = f"AND fct_comm.storefront_name = '{storefront_name}'" if storefront_name else ""

    sku_filter = ""
    if sku_allowlist:
        sku_allowlist_str = "', '".join(sku_allowlist)
        sku_filter = f"AND fct_comm.sku in ('{sku_allowlist_str}')"

    sql_commerce = f"""
        --sql
            SELECT DISTINCT
                fct_comm.session_id,
                fct_comm.order_id,
                COALESCE(LTRIM(dim_comm.code, '0'), CAST(fct_comm.store_id as string)) as store_code,
                fct_comm.created_at,
                fct_comm.user_id,
                fct_comm.sku,
                fct_comm.quantity AS quantity,
                Coalesce(fct_comm.quantity * fct_comm.price, 0) AS item_total_amount
            FROM `arched-photon-194421.DWH.fct_commerce_orders_consolidate` fct_comm
            LEFT JOIN `arched-photon-194421.DWH.dim_commerce_headless_storefront_customer` dim_comm
            ON dim_comm.id = fct_comm.store_id
            WHERE fct_comm.status = 'CONFIRMED'
                AND fct_comm.bot_id = @bot_id
                {storefront_condition}
                AND fct_comm.created_at BETWEEN @start_date AND @end_date
                {sku_filter}
        --endsql
        """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("bot_id", "STRING", bot_id),
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
    )
    data_frame = BIGQUERY_CLIENT.query(sql_commerce, job_config=job_config).to_dataframe()

    data_frame = data_frame.drop_duplicates()
    return data_frame


def get_orders(bot_id, storefront_name=None, start_date=None, end_date=None, sku_allowlist=None):
    df = get_order_items(bot_id, storefront_name, start_date, end_date, sku_allowlist)
    df = aggregated_order_items_in_buyorder(df)
    return df


def get_order_items_from_gcs(file_name, bucket_name="ml-data-dump"):
    # GCS orders are used for historical ERP orders, to be used to train models.
    # The regular path is "gs://ml-data-dump/gai-summit-fake-orders/fake-bot-id_fake-storefront-name.csv"
    # The input file_name example is "gai-summit-fake-orders/fake-bot-id_fake-storefront-name.csv"
    # We have a sample in "data/processed/orders.csv"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    with tempfile.NamedTemporaryFile(mode='w') as temp:
        blob.download_to_filename(temp.name)

        df = pd.read_csv(temp.name)
        return df

    return None

def get_order_items_from_csv(file_name):
    df = pd.read_csv(file_name)
    return df
