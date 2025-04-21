import os
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
# 嘗試載入 .env 檔案
dotenv_loaded = load_dotenv()

# 檢查是否成功載入
if not dotenv_loaded:
    print("❌ .env 檔案載入失敗！請確認檔案存在並格式正確。")
else:
    print("✅ .env 檔案載入成功！")

# 從 .env 取得 API 金鑰
Groq_api_key =os.getenv("Groq_API_KEY")
print(Groq_api_key)
# 檢查是否有設定 API 金鑰
if not Groq_api_key:
    raise ValueError("❌ 未找到Groq API 金鑰")

# API 端點
Groq_base_URL = "https://api.groq.com/openai/v1"

# 預設使用的模型
MODEL = "llama3-70b-8192"

os.environ['OPENAI_API_KEY']= Groq_api_key