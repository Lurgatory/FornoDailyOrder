from config import (
    today,
    forno_warehouses_info_path,
    package_list_path,
    carton_dimension_path,
    dd_result_folder_path,
)
import pandas as pd
import os


def dd_am_csv_df_generator(output_df, input_dd_daily_order_df):
    # Enter the data from THD daily order on server to AM out of an area csv file on local
    output_df["ItemDescription"] = ""
    output_df["ServiceType"] = "DELIVERY"
    output_df["PickupCity"] = input_dd_daily_order_df["pickupcity"]
    output_df["PickupDate"] = f"{today.month}-{today.day}-{today.year}"
    output_df["SpecialInstructions"] = input_dd_daily_order_df["document number"]
    output_df["BolNo"] = input_dd_daily_order_df["bolno"]
    output_df["PONo"] = input_dd_daily_order_df["memo (main)"]
    output_df["ConsigneeName"] = input_dd_daily_order_df["consigneename"]
    output_df["ConsigneeAddr1"] = input_dd_daily_order_df["consigneeaddr1"]
    output_df["ConsigneeAddr2"] = input_dd_daily_order_df["consigneeaddr2"]
    output_df["ConsigneeCity"] = input_dd_daily_order_df["consigneecity"]
    output_df["ConsigneeSt"] = input_dd_daily_order_df["consigneest"]
    output_df["ConsigneeZip"] = input_dd_daily_order_df["consigneezip"]
    output_df["ConsigneePhone"] = input_dd_daily_order_df["consigneephone"]
    output_df["ConsigneeEmail"] = input_dd_daily_order_df["email"]
    output_df["ModelNo or Service KeyWord"] = input_dd_daily_order_df["item"]
    output_df["Qty"] = input_dd_daily_order_df["quantity"]

    # Enter warehouse info
    warehouses_info_df = pd.read_csv(forno_warehouses_info_path)
    warehouses_info = warehouses_info_df["WarehouseCity"].dropna().unique()
    for warehouse_info in warehouses_info:
        warehouse_info_row = warehouses_info_df[
            warehouses_info_df["WarehouseCity"] == warehouse_info
        ]
        if warehouse_info in ["Santa Fe Springs", "Dayton"]:
            output_df.loc[output_df["PickupCity"] == warehouse_info, "Inventory"] = (
                "Yes"
            )
        else:
            output_df.loc[output_df["PickupCity"] == warehouse_info, "Inventory"] = "No"
        output_df.loc[output_df["PickupCity"] == warehouse_info, "PickupAddress1"] = (
            warehouse_info_row["WarehouseAddress"].values[0]
        )
        output_df.loc[output_df["PickupCity"] == warehouse_info, "PickupState"] = (
            warehouse_info_row["WarehouseState"].values[0]
        )
        output_df.loc[output_df["PickupCity"] == warehouse_info, "PickupZip"] = (
            warehouse_info_row["WarehouseZipCode"].values[0]
        )
        output_df.loc[output_df["PickupCity"] == warehouse_info, "PickupPhone"] = (
            warehouse_info_row["WarehousePhoneNumber"].values[0]
        )
        output_df.loc[output_df["PickupCity"] == warehouse_info, "PickupAddressee"] = (
            warehouse_info_row["WarehouseName"].values[0]
        )

    # Expand the row if quantity is more than 1
    output_df["Qty"] = output_df["Qty"].fillna(1).astype(int)
    expand_df = output_df.loc[output_df.index.repeat(output_df["Qty"])].copy()
    expand_df["Qty"] = 1
    output_df = expand_df.reset_index(drop=True)

    # Find package unit first
    package_list_df = pd.read_csv(package_list_path)
    package_dict = (
        package_list_df.groupby("Package products")["Relationships"]
        .apply(list)
        .to_dict()
    )

    expanded_rows = []
    for _, row in output_df.iterrows():
        sku = row["ModelNo or Service KeyWord"]
        qty = row["Qty"] if pd.notna(row["Qty"]) else 1

        if sku in package_dict:
            for component in package_dict[sku]:
                for _ in range(qty):
                    new_row = row.copy()
                    new_row["ModelNo or Service KeyWord"] = component
                    new_row["Qty"] = 1
                    expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)

    output_df = pd.DataFrame(expanded_rows)

    # Fill
    carton_dimension_df = pd.read_csv(carton_dimension_path)
    skus = carton_dimension_df["SKU"].dropna().unique()

    # Validated all skus in out_put_df if they exist in SKU list
    missing_sku_df = output_df[~output_df["ModelNo or Service KeyWord"].isin(skus)]

    if not missing_sku_df.empty:
        missing_file = os.path.join(dd_result_folder_path, "Missing.csv")
        if os.path.exists(missing_file):
            existing_df = pd.read_csv(missing_file)
            combined_df = pd.concat(
                [existing_df, missing_sku_df], ignore_index=True
            ).drop_duplicates()
        else:
            combined_df = missing_sku_df
        combined_df.to_csv(missing_file, index=False)

    for sku in skus:
        carton_dimension_row = carton_dimension_df[carton_dimension_df["SKU"] == sku]
        output_df.loc[
            output_df["ModelNo or Service KeyWord"] == sku, "ItemDescription"
        ] = carton_dimension_row["Label"].values[0]
        output_df.loc[output_df["ModelNo or Service KeyWord"] == sku, "Pallets"] = (
            carton_dimension_row["Pallets"].values[0]
        )
        output_df.loc[output_df["ModelNo or Service KeyWord"] == sku, "Length"] = (
            carton_dimension_row["Depth"].values[0]
        )
        output_df.loc[output_df["ModelNo or Service KeyWord"] == sku, "Width"] = (
            carton_dimension_row["Width"].values[0]
        )
        output_df.loc[output_df["ModelNo or Service KeyWord"] == sku, "Height"] = (
            carton_dimension_row["Height"].values[0]
        )
        output_df.loc[output_df["ModelNo or Service KeyWord"] == sku, "Weight"] = (
            carton_dimension_row["Weight"].values[0]
        )

    return output_df
