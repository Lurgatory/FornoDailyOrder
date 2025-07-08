import os
from config import thd_result_folder_path, today


def not_am_carrier(input_df):
    carriers = input_df["carrier name"].dropna().unique()

    for carrier in carriers:
        carrier_df = input_df[input_df["carrier name"] == carrier]

        # Get a unique warehouse list from each carrier
        warehouses = carrier_df["location"].dropna().unique()
        for warehouse in warehouses:
            warehouse_df = carrier_df[carrier_df["location"] == warehouse]

            if warehouse_df.empty:
                continue

            # Sanitize folder and file names to avoid illegal characters
            safe_carrier_name = carrier.replace(":", "_").replace("/", "_").strip()
            safe_warehouse_name = warehouse.replace(":", "_").replace("/", "_").strip()

            # Create a subfolder for the carrier and warehouse
            carrier_folder = os.path.join(
                thd_result_folder_path, "Other", safe_carrier_name, safe_warehouse_name
            )
            os.makedirs(carrier_folder, exist_ok=True)

            # Save the filtered DataFrame to CSV
            non_am_transport_file_path = os.path.join(
                carrier_folder,
                f"THD {safe_warehouse_name} {safe_carrier_name} {today.month}-{today.day}-{today.year}.csv",
            )
            warehouse_df.to_csv(non_am_transport_file_path, index=False)
