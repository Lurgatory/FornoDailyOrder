import pandas as pd
import os
from config import (
    thd_daily_order_folder_path,
    thd_result_folder_path,
    am_deliverable_zip_code_list_path,
)
from utils.thd_am_csv_generator import out_am_csv, in_am_csv
from utils.thd_not_am_carrier import not_am_carrier
from utils.file_utils import combine_files

# Prepare empty dataframes to collect all data
all_thd_daily_files_df = pd.DataFrame()

# Check the result folder path if it is existed
os.makedirs(thd_result_folder_path, exist_ok=True)

# Read each file in the folder
thd_daily_files = [
    f for f in os.listdir(thd_daily_order_folder_path) if f.endswith(".csv")
]

# Process all AM Transport
# Get postal code list
zipcode_df = pd.read_csv(am_deliverable_zip_code_list_path)
zipcode_set = set(zipcode_df["ZipCode"])

all_thd_daily_files_df = combine_files(
    thd_daily_files, thd_daily_order_folder_path, all_thd_daily_files_df
)

all_other_carriers_order_df = all_thd_daily_files_df[
    all_thd_daily_files_df["carrier name"].astype(str).str.strip().str.lower()
    != "am transport"
]

all_am_transport_df = all_thd_daily_files_df[
    all_thd_daily_files_df["carrier name"].astype(str).str.strip().str.lower()
    == "am transport"
]
all_am_quote_orders_df = all_am_transport_df[
    ~all_am_transport_df["shipto postal code"].isin(zipcode_set)
]
all_am_deliverable_orders_df = all_am_transport_df[
    all_am_transport_df["shipto postal code"].isin(zipcode_set)
]

not_am_carrier(all_other_carriers_order_df)
out_am_csv(all_am_quote_orders_df)
in_am_csv(all_am_deliverable_orders_df)
