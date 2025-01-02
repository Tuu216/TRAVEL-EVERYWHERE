const attractions = {
    "自然景點": ["台中公園", "大坑風景區", "高美濕地"],
    "文化景點": ["國立台灣美術館", "台中文化創意產業園區"],
    "購物": ["逢甲夜市", "一中街商圈"],
    "美食": ["宮原眼科", "第四信用合作社"]
};

function getRecommendation(category) {
    const recommendationDiv = document.getElementById('recommendation');
    const recommendations = attractions[category] || ["抱歉，沒有找到相關的景點。"];
    recommendationDiv.innerHTML = recommendations.join(', ');
}