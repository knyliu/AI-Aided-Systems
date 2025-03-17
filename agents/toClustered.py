import pandas as pd
import os
import glob

def split_into_clusters(input_dir="output_csv", output_dir="clustered_csv"):
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 讀取所有 Depth_i_Epoch_j.csv 檔案
    csv_files = glob.glob(os.path.join(input_dir, "Depth_*_Epoch_*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # 提取檔名資訊
        filename = os.path.basename(file)
        depth, epoch = filename.split("_")[1], filename.split("_")[3]

        # 確保 Cluster_Value 欄位存在
        if "Cluster_Value" not in df.columns:
            print(f"Skipping {file}: No Cluster_Value column found")
            continue
        
        # 依照 Cluster_Value 分群
        for cluster_id, cluster_df in df.groupby("Cluster_Value"):
            output_filename = os.path.join(output_dir, f"Depth_{depth}_Epoch_{epoch}_Cluster_{cluster_id}.csv")
            cluster_df.to_csv(output_filename, index=False, encoding="utf-8")
            print(f"Saved: {output_filename}")

if __name__ == "__main__":
    split_into_clusters()
