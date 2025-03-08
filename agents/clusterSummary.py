import pandas as pd
import os
import glob
from llm import get_llm_response  # 引入 llm.py 的函數

# 系統提示詞
# 系統提示詞
SYSTEM_PROMPT = """你是一位專業的區塊鏈分析師，負責處理區塊鏈交易數據。
請閱讀以下的 CSV 內容，這些數據來自同一個交易群組，請完整地描述這些交易的特性，並說明這個群組的共同處。
 **說明：部分欄位已被重新編碼**
- `Hash`、`From`、`To` 欄位的原始內容過長，已被重新編碼為較短的唯一 ID：
  - `Hash`（交易哈希值） ➝ `H0`, `H1`, `H2`, ...
  - `From`（交易發送方） ➝ `F0`, `F1`, `F2`, ...
  - `To`（交易接收方） ➝ `T0`, `T1`, `T2`, ...
  這些 ID 仍然是唯一的，但不代表實際地址。
"""


def summarize_clustered_data(input_dir="clustered_csv", output_dir="clusterSummary"):
    """處理所有 cluster CSV，並產生對應的 LLM 摘要"""
    os.makedirs(output_dir, exist_ok=True)  # 確保輸出目錄存在

    csv_files = glob.glob(os.path.join(input_dir, "Depth_*_Epoch_*_Cluster_*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)

        # 取得檔名資訊
        filename = os.path.basename(file)
        depth, epoch, cluster = filename.split("_")[1], filename.split("_")[3], filename.split("_")[5].split(".")[0]

        # 轉換 CSV 內容為文字摘要格式
        csv_content = df.head(10).to_string(index=False)  # 取前 10 筆資料
        prompt = f"{SYSTEM_PROMPT}\n\n以下是數據樣本：\n{csv_content}\n\n請產生摘要："

        # 調用 LLM
        response = get_llm_response(prompt)

        # 儲存摘要
        output_filename = os.path.join(output_dir, f"summary_Depth_{depth}_Epoch_{epoch}_Cluster_{cluster}.txt")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"Saved summary: {output_filename}")

if __name__ == "__main__":
    summarize_clustered_data()
