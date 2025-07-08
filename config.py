import os
from datetime import datetime

today = datetime.today()

# Reference Data Path
am_deliverable_zip_code_list_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "AMDeliverableZip.csv"
)
am_csv_template_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "AMCSVTemplate.csv"
)
forno_warehouses_info_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "FornoWarehouse.csv"
)
carton_dimension_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "CartonDimension.csv"
)
package_list_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "PackageList.csv"
)
ground_label_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "GroundLabelTemplate.csv"
)

# THD Path
thd_daily_order_folder_path = (
    r"\\SRV-AD01\Folder Redirection\SLu\Documents\THD_Daily_Order"
)
thd_result_folder_path = rf"\\SRV-AD01\Folder Redirection\SLu\Desktop\Buffer\{today.year}\{today.strftime('%b')}\{today.day}\THD"

# DD Path
dd_daily_order_folder_path = (
    r"\\SRV-AD01\Folder Redirection\SLu\Documents\DD_Daily_Order"
)
dd_gl_ofz_file_path = os.path.join(dd_daily_order_folder_path, "GL_OFZ_List")
dd_result_folder_path = rf"\\SRV-AD01\Folder Redirection\SLu\Desktop\Buffer\{today.year}\{today.strftime('%b')}\{today.day}\SHOP"
dd_pending_invoice_file_path = (
    r"Z:\User\Order Entry User\Michael Daily Orders\Orders\PendingOrders.xlsx"
)
