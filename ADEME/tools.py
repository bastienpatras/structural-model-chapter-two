import time
from io import StringIO

import pandas as pd
import requests
from google.cloud import storage


def gcs_file_exists(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.exists()


def read_csv_from_gcs(bucket_name, file_name, client=None):
    if client is None:
        client = storage.Client()

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # More efficient for large files
    with blob.open("r") as f:
        df = pd.read_csv(f)

    return df


def export_to_gcs(bucket_name, blob_name, new_df):
    """
    Appends new data to an existing CSV file in GCS (without duplicates), or creates a new file.

    Parameters:
    - bucket_name (str): Name of GCS bucket
    - blob_name (str): Path to file in bucket
    - new_df (pd.DataFrame): New data to upload
    """

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    retries = 5
    timeout = 600  # 10 minutes timeout for both download and upload

    def upload_with_retry(blob, data, retries, timeout):
        for i in range(retries):
            try:
                blob.upload_from_string(data, content_type="text/csv", timeout=timeout)
                return
            except requests.exceptions.RequestException as e:
                print(f"Upload attempt {i + 1} failed: {e}")
                time.sleep(2**i)  # Exponential backoff
        raise Exception("Upload failed after several retries.")

    if blob.exists():
        # Download and read existing data with increased timeout
        csv_data = blob.download_as_text(timeout=timeout)
        existing_df = pd.read_csv(StringIO(csv_data))

        # Concatenate and drop duplicates
        combined_df = pd.concat(
            [existing_df, new_df], ignore_index=True
        ).drop_duplicates()

        # Save updated data to a buffer
        csv_buffer = StringIO()
        combined_df.to_csv(csv_buffer, index=False)

        # Upload with retries
        upload_with_retry(blob, csv_buffer.getvalue(), retries, timeout)
        print(f"📂 Appended data to existing file: gs://{bucket_name}/{blob_name}")
    else:
        # Write new CSV
        csv_buffer = StringIO()
        new_df.to_csv(csv_buffer, index=False)

        # Upload with retries
        upload_with_retry(blob, csv_buffer.getvalue(), retries, timeout)
        print(f"📁 Created new file: gs://{bucket_name}/{blob_name}")
