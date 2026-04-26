from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 프론트엔드(웹 브라우저)에서 오는 요청을 허용하는 보안 설정 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEOUL_API_KEY = "6e50616f7430367936325a4d635a6e"

area_mapping = {
    "홍대": "홍대 관광특구", 
    "명동": "명동 관광특구",
    "강남": "강남역",
    "성수": "성수카페거리"
}

@app.get("/api/recommend/{area_key}")
def get_realtime_data(area_key: str):
    official_area_name = area_mapping.get(area_key, area_key)
    
    url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/citydata/1/5/{official_area_name}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        city_data = data.get("CITYDATA", {})
        live_data = city_data.get("LIVE_PPLTN_STTS", [])[0]
        
        congestion_lvl = live_data.get("AREA_CONGEST_LVL", "데이터 없음")
        congestion_msg = live_data.get("AREA_CONGEST_MSG", "현재 혼잡도 메시지를 불러올 수 없습니다.")
        
    except Exception as e:
        print(f"API 호출 에러: {e}")
        return {
            "status_icon": "⚠️",
            "congestion": "오류",
            "recommend_message": "서울시 데이터 서버와 연결할 수 없거나 API 키가 잘못되었습니다."
        }

    alt_courses = {
        "홍대": "망원동 한적한 카페거리",
        "명동": "남산 둘레길 및 후암동 루프탑",
        "강남": "양재천 수변 산책로",
        "성수": "서울숲 북측 조용한 골목"
    }
    recommend_place = alt_courses.get(area_key, "인근 조용한 골목")

    if congestion_lvl in ["붐빔", "매우 붐빔"]:
        status_icon = "🚨"
        message = f"<strong>[{congestion_msg}]</strong><br><br>인파가 많아 복잡합니다. 인접한 <strong>'{recommend_place}'</strong>(으)로 데이트 코스를 변경해보는 건 어떨까요?"
    else:
        status_icon = "✨"
        message = f"<strong>[{congestion_msg}]</strong><br><br>비교적 쾌적한 상태이니 해당 지역에서 그대로 데이트를 즐기셔도 좋습니다!"

    return {
        "area": area_key,
        "status_icon": status_icon,
        "congestion": congestion_lvl,
        "recommend_message": message
    }