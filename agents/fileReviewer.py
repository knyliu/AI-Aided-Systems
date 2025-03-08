import os
import re
import json
import requests
from dotenv import load_dotenv

class FileReviewer:
    def __init__(self, allowed_dirs=None, token_threshold=1000):
        """
        初始化時，根目錄固定為專案的根目錄（假設此程式放在專案的子目錄中，
        則專案根目錄為此檔案的上層目錄）。
        
        allowed_dirs: 指定一個包含可探索目錄的列表（相對於專案根目錄）。
                      例如：["docs", "data", "src"]。
                      若為 None 或空列表，則只檢查根目錄中的檔案，不做遞迴掃描。
        token_threshold: 當檔案內容 token 數超過此門檻時，會呼叫 Gemini 進行摘要。
        """
        # 設定專案根目錄（此處假設專案根目錄為此檔案所在目錄的上層）
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.token_threshold = token_threshold
        self.allowed_dirs = allowed_dirs if allowed_dirs is not None else []

        # 讀取 .env 檔中的 GEMINI_API_KEY
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise Exception("請在 .env 檔中設定 GEMINI_API_KEY")
    
    def build_file_tree(self, current_path):
        """
        遞迴建立檔案樹，回傳一個字典結構，包含目錄與檔案資訊
        """
        tree = {
            "name": os.path.basename(current_path),
            "path": os.path.relpath(current_path, self.root_dir),
            "type": "directory",
            "children": []
        }
        try:
            entries = os.listdir(current_path)
        except Exception:
            # 若無法讀取則回傳空的 children
            return tree
        
        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                tree["children"].append(self.build_file_tree(full_path))
            else:
                tree["children"].append({
                    "name": entry,
                    "path": os.path.relpath(full_path, self.root_dir),
                    "type": "file"
                })
        return tree

    def get_file_structure(self):
        """
        取得專案的檔案結構：
          - 若 allowed_dirs 有指定，只探索這些資料夾（遞迴建立檔案樹）。
          - 若 allowed_dirs 為空，則僅回傳根目錄中的檔案（不遞迴）。
        回傳的結果為一個樹狀結構的字典。
        """
        trees = []
        if self.allowed_dirs:
            for d in self.allowed_dirs:
                full_path = os.path.join(self.root_dir, d)
                if os.path.exists(full_path) and os.path.isdir(full_path):
                    trees.append(self.build_file_tree(full_path))
            return {
                "name": os.path.basename(self.root_dir),
                "path": ".",
                "type": "directory",
                "children": trees
            }
        else:
            # 若沒有指定 allowed_dirs，僅回傳根目錄中的檔案
            children = []
            for entry in os.listdir(self.root_dir):
                full_path = os.path.join(self.root_dir, entry)
                if os.path.isfile(full_path):
                    children.append({
                        "name": entry,
                        "path": entry,
                        "type": "file"
                    })
            return {
                "name": os.path.basename(self.root_dir),
                "path": ".",
                "type": "directory",
                "children": children
            }
    
    def call_gemini(self, prompt_text):
        """
        呼叫 Gemini API，傳入 prompt_text，並回傳 API 的 JSON 回應
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Gemini API 呼叫失敗：{response.text}")
    
    def extract_json_from_response(self, response):
        """
        解析 Gemini API 回應，擷取 JSON 格式的內容，回傳字典
        """
        try:
            # 先確認 response 結構是否符合預期
            if "candidates" not in response or not response["candidates"]:
                print("⚠️ Gemini 回應格式異常，未找到 candidates，回傳空 JSON。")
                return {}

            # 取得 Gemini 回應的主要內容
            output_text = response["candidates"][0]["content"]["parts"][0]["text"]

            # 嘗試擷取 JSON 區段
            match = re.search(r"```json\s*(.*?)\s*```", output_text, re.DOTALL)
            if match:
                json_text = match.group(1).strip()

                try:
                    return json.loads(json_text)  # 解析為 JSON
                except json.JSONDecodeError as e:
                    print(f"⚠️ 解析 JSON 時發生錯誤: {e}")
                    return {}

            print("⚠️ Gemini 回應沒有 JSON 格式的資料，回傳空 JSON。")
            return {}

        except Exception as e:
            print(f"⚠️ 提取 Gemini 回應時發生未知錯誤: {e}")
            return {}
    
    def choose_file(self, query):
        """
        傳入自然語言查詢，根據專案檔案架構資訊透過 Gemini API 決定最相關的檔案，
        預期回傳 JSON 格式，如：{"selected_files": ["檔案相對路徑"]}
        """
        file_structure = self.get_file_structure()
        file_structure_str = json.dumps(file_structure, ensure_ascii=False, indent=2)
        prompt = (
            f"以下為專案的檔案架構：\n{file_structure_str}\n\n"
            f"使用者查詢：'{query}'。\n"
            "請從上述檔案架構中選出最符合查詢需求的檔案，請只回覆一個 JSON 格式，格式為：\n"
            "```json\n"
            "{\"selected_files\": [\"檔案相對路徑\"]}\n"
            "```"
        )
        gemini_response = self.call_gemini(prompt)
        return self.extract_json_from_response(gemini_response)
    
    def open_file(self, file_rel_path):
        """
        根據檔案相對路徑讀取檔案內容，回傳內容作為字串
        """
        file_path = os.path.join(self.root_dir, file_rel_path)
        if not os.path.exists(file_path):
            raise Exception(f"檔案 {file_rel_path} 不存在於 {self.root_dir}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    
    def process_file_content(self, content):
        """
        計算內容的 token 數（以空白分割計算單字數），
        若超過門檻則呼叫 Gemini 進行摘要，否則保留原始內容
        """
        tokens = len(content.split())
        if tokens > self.token_threshold:
            prompt = (
                "請對下列內容做摘要，摘要結果請用 JSON 格式回覆，格式為：\n"
                "```json\n"
                "{\"summary\": \"摘要內容\"}\n"
                "```。\n"
                "以下為內容：\n" + content
            )
            gemini_response = self.call_gemini(prompt)
            summary_json = self.extract_json_from_response(gemini_response)
            if "summary" in summary_json:
                return summary_json["summary"]
            else:
                raise Exception("Gemini 回應中未找到 'summary' 欄位")
        else:
            return content

    def get_file_info(self, query):
        """
        高階介面：根據自然語言查詢決定要檢視的檔案，
        讀取檔案內容，並依內容長度決定是否摘要後回傳最終檔案資訊
        """
        selection = self.choose_file(query)
        if "selected_files" in selection and len(selection["selected_files"]) > 0:
            file_rel_path = selection["selected_files"][0]
            content = self.open_file(file_rel_path)
            final_content = self.process_file_content(content)
            return {
                "file": file_rel_path,
                "content": final_content
            }
        else:
            raise Exception("Gemini 無法選出合適的檔案")

# 範例用法：
if __name__ == '__main__':
    # 例如只想探索專案根目錄下的 "docs" 與 "data" 資料夾
    reviewer = FileReviewer(allowed_dirs=["personalInfo"])

    query = "我想查看關於yen ku liu的資料"
    try:
        file_info = reviewer.get_file_info(query)
        print("最終檔案資訊：")
        print(f"檔案名稱：{file_info['file']}")
        print("內容：")
        print(file_info['content'])
    except Exception as e:
        print(f"發生錯誤：{e}")
