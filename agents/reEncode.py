import pandas as pd
import os
import json

def re_encode_data(input_file="kmeans_clustered_results.csv", output_file="data_encoded.csv", map_file="encoding_map.json"):
    """ 重新編碼 Hash、From、To 欄位，並產生新的 data_encoded.csv """

    # 讀取 CSV
    df = pd.read_csv(input_file)

    # 需要重新編碼的欄位
    columns_to_encode = ["Hash", "From", "To"]
    encoding_map = {}

    # 針對每個欄位生成唯一 ID
    for col in columns_to_encode:
        unique_values = df[col].unique()
        value_to_id = {value: f"{col[:1]}{idx}" for idx, value in enumerate(unique_values)}  # 產生 ID
        encoding_map[col] = value_to_id

        # 取代原本的值
        df[col] = df[col].map(value_to_id)

    # 儲存新的 CSV
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Saved encoded data: {output_file}")

    # 儲存編碼對應關係
    with open(map_file, "w", encoding="utf-8") as f:
        json.dump(encoding_map, f, indent=4)
    print(f"Saved encoding map: {map_file}")

if __name__ == "__main__":
    re_encode_data()
