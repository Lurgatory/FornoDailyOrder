from config import (
    today,
    forno_warehouses_info_path,
    package_list_path,
    carton_dimension_path,
    thd_result_folder_path,
)
import pandas as pd
import os


def thd_am_csv_df_generator(output_df, input_thd_daily_order_df):
    # Enter the data from THD daily order on server to AM out of an area csv file on local
    output_df["ItemDescription"] = ""
    output_df["ServiceType"] = "DELIVERY"
    output_df["PickupAddressee"] = input_thd_daily_order_df["location"]
    output_df["PickupDate"] = f"{today.month}-{today.day}-{today.year}"
    output_df["BolNo"] = input_thd_daily_order_df["po number"]
    output_df["ConsigneeName"] = input_thd_daily_order_df["shipto name"]
    output_df["ConsigneeAddr1"] = input_thd_daily_order_df["shipto address1"]
    output_df["ConsigneeAddr2"] = input_thd_daily_order_df["shipto address2"]
    output_df["ConsigneeCity"] = input_thd_daily_order_df["shipto city"]
    output_df["ConsigneeSt"] = input_thd_daily_order_df["shipto state_x"]
    output_df["ConsigneeZip"] = input_thd_daily_order_df["shipto postal code"]
    output_df["ConsigneePhone"] = input_thd_daily_order_df["shipto day phone"]
    output_df["ModelNo or Service KeyWord"] = input_thd_daily_order_df["vendor sku"]
    output_df["Qty"] = input_thd_daily_order_df["quantity"]

    # Validate the data and modify the output df
    # If consignee address is store, add "SHIP TO STORE" in the special instruction column
    if "SpecialInstructions" not in output_df.columns:
        output_df["SpecialInstructions"] = ""
    store_consignee_address = (
        output_df["ConsigneeAddr1"].astype(str).str.contains("C/O", na=False)
    )
    output_df.loc[store_consignee_address, "SpecialInstructions"] = "SHIP TO STORE"

    # Enter the data
    warehouses_info_df = pd.read_csv(forno_warehouses_info_path)
    warehouses_info = warehouses_info_df["Warehouse"].dropna().unique()
    for warehouse_info in warehouses_info:
        warehouse_info_row = warehouses_info_df[
            warehouses_info_df["Warehouse"] == warehouse_info
        ]
        if warehouse_info == "Los Angeles AM":
            output_df.loc[
                output_df["PickupAddressee"] == warehouse_info, "Inventory"
            ] = "Yes"
        else:
            output_df.loc[
                output_df["PickupAddressee"] == warehouse_info, "Inventory"
            ] = "No"
        output_df.loc[
            output_df["PickupAddressee"] == warehouse_info, "PickupAddress1"
        ] = warehouse_info_row["WarehouseAddress"].values[0]
        output_df.loc[output_df["PickupAddressee"] == warehouse_info, "PickupCity"] = (
            warehouse_info_row["WarehouseCity"].values[0]
        )
        output_df.loc[output_df["PickupAddressee"] == warehouse_info, "PickupState"] = (
            warehouse_info_row["WarehouseState"].values[0]
        )
        output_df.loc[output_df["PickupAddressee"] == warehouse_info, "PickupZip"] = (
            warehouse_info_row["WarehouseZipCode"].values[0]
        )
        output_df.loc[output_df["PickupAddressee"] == warehouse_info, "PickupPhone"] = (
            warehouse_info_row["WarehousePhoneNumber"].values[0]
        )
        output_df.loc[
            output_df["PickupAddressee"] == warehouse_info, "PickupAddressee"
        ] = warehouse_info_row["WarehouseName"].values[0]

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
        missing_file = os.path.join(thd_result_folder_path, "Missing.csv")
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
