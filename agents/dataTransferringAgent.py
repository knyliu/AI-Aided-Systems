import pandas as pd
import os

def transfer_data(input_file="kmeans_clustered_results.csv", output_dir="output_csv"):
    # 讀取 kmeans_clustered_results.csv
    df = pd.read_csv(input_file)

    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 定義固定欄位
    base_columns = ["layer", "BlockNumber", "TimeStamp", "Hash", "From", "To", "Value", "TokenName", "TokenSymbol"]

    # 找出所有 Cluster_Depth_i_Epoch_j 欄位
    cluster_columns = [col for col in df.columns if col.startswith("Cluster_Depth_")]

    # 解析不同的 Depth 和 Epoch
    depth_epoch_set = set()
    for col in cluster_columns:
        parts = col.split("_")
        depth = parts[2]
        epoch = parts[4]
        depth_epoch_set.add((depth, epoch))

    # 依照 Depth 和 Epoch 建立獨立的 CSV
    for depth, epoch in sorted(depth_epoch_set, key=lambda x: (int(x[0]), int(x[1]))):
        column_name = f"Cluster_Depth_{depth}_Epoch_{epoch}"
        
        if column_name in df.columns:
            subset_df = df[base_columns + [column_name]].copy()
            subset_df.rename(columns={column_name: "Cluster_Value"}, inplace=True)
            
            output_filename = os.path.join(output_dir, f"Depth_{depth}_Epoch_{epoch}.csv")
            subset_df.to_csv(output_filename, index=False, encoding="utf-8")
            print(f"Saved: {output_filename}")

if __name__ == "__main__":
    transfer_data()
