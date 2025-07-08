import os
from config import dd_result_folder_path, today
from utils import dd_am_csv_df_generator

GL_COLUMNS_TO_DROP = [
    "document number",
    "shopify order id",
    "memo (main)",
    "digital dealer",
    "status",
    "pickupaddress1",
    "pickupaddress2",
    "pickupcity",
    "pickupstate",
    "pickupzip",
    "pickupphone",
]


def export_gl_csv(all_gl_df):
    all_gl_df = all_gl_df.drop(columns=GL_COLUMNS_TO_DROP, axis=1)
    all_gl_df["price"] = None
    output_gl_path = os.path.join(dd_result_folder_path, "GL")
    os.makedirs(output_gl_path, exist_ok=True)
    final_gl_path = os.path.join(
        output_gl_path, f"DD_Forno_GL_RCA_{today.year}-{today.month}-{today.day}.csv"
    )
    all_gl_df.to_csv(final_gl_path, index=False)


def export_ofz_csv(all_ofz_df):
    output_ofz_path = os.path.join(dd_result_folder_path, "OFZ")
    os.makedirs(output_ofz_path, exist_ok=True)
    final_ofz_path = os.path.join(
        output_ofz_path, f"DD_Forno_OFZ_{today.year}-{today.month}-{today.day}.csv"
    )
    all_ofz_df.to_csv(final_ofz_path, index=False)

def export_am_csv(output_am_df,filter_pure_df):
    output_am_df = dd_am_csv_df_generator.dd_am_csv_df_generator(output_am_df, filter_pure_df)

    output_am_path = os.path.join(dd_result_folder_path, "AM")
    os.makedirs(output_am_path, exist_ok=True)

    warehouses = output_am_df["PickupAddressee"].dropna().unique()
    for warehouse in warehouses:
        warehouse_df = output_am_df[output_am_df["PickupAddressee"] == warehouse]
        safe_warehouse_name: str = warehouse.replace(":", "_").replace("/", "_").strip()

        warehouse_path = os.path.join(output_am_path, f"{warehouse}")
        os.makedirs(warehouse_path, exist_ok=True)

        final_result_path = os.path.join(warehouse_path, f"DD {safe_warehouse_name}.csv")
        warehouse_df.to_csv(final_result_path, index=False)