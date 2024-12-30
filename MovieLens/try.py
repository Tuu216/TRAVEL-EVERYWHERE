class TaichungTourGuide:
    def __init__(self, llm):
        self.llm = llm
        self.attractions = {
            "自然景點": ["台中公園", "大坑風景區", "高美濕地"],
            "文化景點": ["國立台灣美術館", "台中文化創意產業園區"],
            "購物": ["逢甲夜市", "一中街商圈"],
            "美食": ["宮原眼科", "第四信用合作社"]
        }

    def recommend(self, preference):
        # 使用LLM來分析用戶的偏好
        response = self.llm.analyze(preference)
        category = self._determine_category(response)
        return self.attractions.get(category, "抱歉，沒有找到相關的景點。")

    def _determine_category(self, response):
        # 假設LLM返回的結果中包含一個類別
        if "自然" in response:
            return "自然景點"
        elif "文化" in response:
            return "文化景點"
        elif "購物" in response:
            return "購物"
        elif "美食" in response:
            return "美食"
        else:
            return None

# 假設有一個LLM的實例
class MockLLM:
    def analyze(self, text):
        # 這是一個簡單的模擬分析
        if "自然" in text:
            return "自然"
        elif "文化" in text:
            return "文化"
        elif "購物" in text:
            return "購物"
        elif "美食" in text:
            return "美食"
        else:
            return "未知"

# 使用範例
llm = MockLLM()
guide = TaichungTourGuide(llm)
user_input = "我想去一些自然景點"
recommendations = guide.recommend(user_input)
print("推薦的景點:", recommendations)