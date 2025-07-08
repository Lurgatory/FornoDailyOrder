import pandas as pd
import os


def combine_files(input_files, input_folder_path, all_df):
    if not input_files:
        print(f"Cannot find files in {input_folder_path}")
    else:
        for csv_file in input_files:
            dd_source_file = os.path.join(str(input_folder_path), str(csv_file))
            df = pd.read_csv(dd_source_file)

            df.columns = df.columns.str.strip().str.lower()

            all_df = pd.concat([all_df, df], ignore_index=True)
    return all_df
