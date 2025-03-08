import os
import glob

# 定義要清除的目錄和檔案類型
OUTPUT_DIRS = ["output_csv", "clustered_csv"]
ENCODED_FILES = ["data_encoded.csv", "encoding_map.json"]
SUMMARY_DIR = "clusterSummary"  # 摘要資料夾

def reset_generated_files():
    """刪除所有被生成的小 CSV 檔案與編碼對應表"""

    # 提示使用者是否確定刪除一般輸出檔案
    confirm_general = input("Are you sure you want to delete all generated CSV files and encoded data? (y/n): ").strip().lower()
    
    if confirm_general == "y":
        # 清除一般 CSV 檔案
        for directory in OUTPUT_DIRS:
            if os.path.exists(directory):
                files = glob.glob(os.path.join(directory, "*.csv"))
                for file in files:
                    os.remove(file)
                print(f"Cleared CSV files in {directory}")

        # 刪除 data_encoded.csv 和 encoding_map.json
        for file in ENCODED_FILES:
            if os.path.exists(file):
                os.remove(file)
                print(f"Deleted {file}")

        print("General reset complete!")
    else:
        print("Skipping general CSV file deletion.")

    # **額外詢問是否刪除 clusterSummary**
    confirm_summary = input("Do you want to delete all generated summaries in clusterSummary? (y/n): ").strip().lower()

    if confirm_summary == "y":
        if os.path.exists(SUMMARY_DIR):
            summary_files = glob.glob(os.path.join(SUMMARY_DIR, "*.txt"))
            for file in summary_files:
                os.remove(file)
            print(f"Cleared summary files in {SUMMARY_DIR}")
        print("Summary reset complete!")
    else:
        print("Keeping summary files.")

if __name__ == "__main__":
    reset_generated_files()
