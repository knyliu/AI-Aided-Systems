import os
import shutil
import agents.epochComparison as epochComparison

# 測試資料夾
TEST_CLUSTER_ANALYSIS_DIR = "test_clusterAnalysis"
TEST_EPOCH_COMPARISON_DIR = "test_epochComparison"

# 測試檔案
TEST_FILE = os.path.join(TEST_CLUSTER_ANALYSIS_DIR, "analysis_Depth_10_Epoch_1.txt")
TEST_OUTPUT_FILE = os.path.join(TEST_EPOCH_COMPARISON_DIR, "comparison_Depth_10.txt")

def setup_test_environment():
    """建立測試環境，確保 clusterAnalysis 內有測試檔案"""
    if not os.path.exists(TEST_CLUSTER_ANALYSIS_DIR):
        os.makedirs(TEST_CLUSTER_ANALYSIS_DIR)

    # 創建測試檔案
    test_content = """
    📌 **Epoch 1 Analysis:**
    這是一個測試摘要，模擬 LLM 產生的交易分群結果。
    Epoch 1 的主要交易特徵是 Token A 活躍，交易量穩定。

    📌 **Epoch 2 Analysis:**
    這是一個測試摘要，模擬 LLM 產生的交易分群結果。
    Epoch 2 的交易模式與 Epoch 1 有差異，Token B 開始增加。
    """
    
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write(test_content)

def cleanup_test_environment():
    """清理測試環境"""
    if os.path.exists(TEST_CLUSTER_ANALYSIS_DIR):
        shutil.rmtree(TEST_CLUSTER_ANALYSIS_DIR)
    if os.path.exists(TEST_EPOCH_COMPARISON_DIR):
        shutil.rmtree(TEST_EPOCH_COMPARISON_DIR)

def test_compare_epochs():
    """測試 epochComparison.py，確保 LLM 正確處理測試檔案"""
    setup_test_environment()

    # 執行測試
    print("🔍 正在測試 Epoch 比較功能...")
    epochComparison.compare_epochs(input_dir=TEST_CLUSTER_ANALYSIS_DIR, output_dir=TEST_EPOCH_COMPARISON_DIR)

    # 檢查是否正確產生了輸出檔案
    assert os.path.exists(TEST_OUTPUT_FILE), f"測試失敗：{TEST_OUTPUT_FILE} 未產生！"

    # 讀取輸出內容
    with open(TEST_OUTPUT_FILE, "r", encoding="utf-8") as f:
        output_content = f.read()
        print("\n✅ 測試成功！以下是 LLM 產生的輸出內容：\n")
        print(output_content)

    # 清理測試資料
    cleanup_test_environment()

if __name__ == "__main__":
    test_compare_epochs()
