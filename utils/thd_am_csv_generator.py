import pandas as pd
import os
from config import am_csv_template_path, today, thd_result_folder_path
from utils import thd_am_csv_df_generator


def generate_am_output_df(input_df):
    am_csv_template_df = pd.read_csv(am_csv_template_path, nrows=0)
    am_csv_template_columns = am_csv_template_df.columns.tolist()
    output_df = pd.DataFrame(columns=am_csv_template_columns)
    output_df = output_df.reindex(index=input_df.index)
    output_df = thd_am_csv_df_generator.thd_am_csv_df_generator(output_df, input_df)
    return output_df


def save_am_csv(base_folder, output_df, filename_prefix, include_ofz=False):
    os.makedirs(base_folder, exist_ok=True)

    if include_ofz:
        am_quote_file_path = os.path.join(
            base_folder, f"{filename_prefix} {today.month}-{today.day}-{today.year}.csv"
        )
        output_df.to_csv(am_quote_file_path, index=False)

    warehouses = output_df["PickupAddressee"].dropna().unique()
    for warehouse in warehouses:
        warehouse_df = output_df[output_df["PickupAddressee"] == warehouse]
        safe_warehouse_name: str = warehouse.replace(":", "_").replace("/", "_").strip()
        carrier_folder: str = os.path.join(base_folder, safe_warehouse_name)
        os.makedirs(carrier_folder, exist_ok=True)

        file_prefix: str = f"THD {'OFZ' if include_ofz else ''} {safe_warehouse_name}"
        am_quote_warehouse_file_path = os.path.join(
            carrier_folder, f"{file_prefix} {today.month}-{today.day}-{today.year}.csv"
        )
        warehouse_df.to_csv(am_quote_warehouse_file_path, index=False)


def out_am_csv(input_df):
    output_df = generate_am_output_df(input_df)
    am_quote_folder = os.path.join(thd_result_folder_path, "AM Quote")
    save_am_csv(am_quote_folder, output_df, "THD AM Quote", include_ofz=True)


def in_am_csv(input_df):
    output_df = generate_am_output_df(input_df)
    am_folder = os.path.join(thd_result_folder_path, "AM")
    save_am_csv(am_folder, output_df, "THD", include_ofz=False)
