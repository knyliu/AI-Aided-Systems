import os
import re
import json
import requests
from dotenv import load_dotenv

class FileReviewer:
    def __init__(self, allowed_dirs=None, token_threshold=1000):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.token_threshold = token_threshold
        self.allowed_dirs = allowed_dirs if allowed_dirs is not None else []

        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise Exception("請在 .env 檔中設定 GEMINI_API_KEY")

    def build_file_tree(self, current_path):
        tree = {
            "name": os.path.basename(current_path),
            "path": os.path.relpath(current_path, self.root_dir),
            "type": "directory",
            "children": []
        }
        try:
            entries = os.listdir(current_path)
        except Exception:
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
        trees = []
        if self.allowed_dirs:
            for d in self.allowed_dirs:
                full_path = os.path.join(self.root_dir, d)
                if os.path.exists(full_path) and os.path.isdir(full_path):
                    trees.append(self.build_file_tree(full_path))
            return {"name": os.path.basename(self.root_dir), "path": ".", "type": "directory", "children": trees}
        else:
            children = []
            for entry in os.listdir(self.root_dir):
                full_path = os.path.join(self.root_dir, entry)
                if os.path.isfile(full_path):
                    children.append({"name": entry, "path": entry, "type": "file"})
            return {"name": os.path.basename(self.root_dir), "path": ".", "type": "directory", "children": children}

    def call_gemini(self, prompt_text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Gemini API 呼叫失敗：{response.text}")

    def extract_json_from_response(self, response):
        try:
            if "candidates" not in response or not response["candidates"]:
                return {}
            output_text = response["candidates"][0]["content"]["parts"][0]["text"]
            match = re.search(r"```json\s*(.*?)\s*```", output_text, re.DOTALL)
            if match:
                json_text = match.group(1).strip()
                return json.loads(json_text)
            return {}
        except Exception as e:
            return {}

    def choose_files(self, query):
        file_structure = self.get_file_structure()
        file_structure_str = json.dumps(file_structure, ensure_ascii=False, indent=2)
        prompt = (
            f"以下為專案的檔案架構：\n{file_structure_str}\n\n"
            f"使用者查詢：'{query}'。\n"
            "請選出符合查詢需求的 **一個或多個** 檔案，並確保格式為有效的 JSON：\n"
            "```json\n"
            "{\n"
            "  \"selected_files\": [\n"
            "    \"檔案1相對路徑\",\n"
            "    \"檔案2相對路徑\",\n"
            "    \"檔案3相對路徑\"\n"
            "  ]\n"
            "}\n"
            "```\n"
            "請確保回覆格式正確，並且僅回傳 JSON 結果，不要提供額外的解釋。"
        )
        gemini_response = self.call_gemini(prompt)
        return self.extract_json_from_response(gemini_response)

    def open_file(self, file_rel_path):
        file_path = os.path.join(self.root_dir, file_rel_path)
        if not os.path.exists(file_path):
            raise Exception(f"❌ 檔案 {file_rel_path} 不存在於 {self.root_dir}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def process_file_content(self, content):
        tokens = len(content.split())
        if tokens > self.token_threshold:
            prompt = (
                "請對下列內容做摘要，並用 JSON 回覆：\n"
                "```json\n"
                "{ \"summary\": \"摘要內容\" }\n"
                "```\n"
                "以下為內容：\n" + content
            )
            gemini_response = self.call_gemini(prompt)
            summary_json = self.extract_json_from_response(gemini_response)
            return summary_json.get("summary", content)
        return content

    def get_file_info(self, query):
        selection = self.choose_files(query)
        if "selected_files" in selection and selection["selected_files"]:
            files_info = []
            for file_rel_path in selection["selected_files"]:
                try:
                    content = self.open_file(file_rel_path)
                    final_content = self.process_file_content(content)
                    files_info.append({"file": file_rel_path, "content": final_content})
                except Exception as e:
                    print(f"⚠️ 無法讀取 {file_rel_path}，錯誤：{e}")
            
            if not files_info:
                raise Exception("❌ 無法成功讀取任何檔案")
            
            return files_info  # 🚀 確保多個檔案資訊都被傳遞
        else:
            raise Exception("❌ Gemini 無法選出合適的檔案")

if __name__ == '__main__':
    reviewer = FileReviewer(allowed_dirs=["clusterSummary"])
    query = "比較同樣為深度2epoch1時，每一個Cluster的差異"

    try:
        file_infos = reviewer.get_file_info(query)
        print("🔍 最終選定的檔案資訊：")
        for file_info in file_infos:
            print(f"\n📂 檔案名稱：{file_info['file']}")
            print("📜 內容：")
            print(file_info['content'])
            print("=" * 80)  # 分隔線，清楚顯示多個檔案內容

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
