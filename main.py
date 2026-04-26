import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 프론트엔드 통신 허용 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서울시 API 키
SEOUL_API_KEY = "4c4663594b3036793731476d445950"

@app.get("/api/recommend/{area_name}")
async def get_live_data(area_name: str):
    """서울시 실시간 도시데이터를 가져오는 API"""
    try:
        url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/citydata/1/5/{area_name}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        city_data = data.get("CITYDATA", {})
        
        # 1. 혼잡도 정보 추출
        live_ppltn = city_data.get("LIVE_PPLTN_STTS", [{}])[0]
        congestion = live_ppltn.get("AREA_CONGEST_LVL", "정보 없음")
        congest_msg = live_ppltn.get("AREA_CONGEST_MSG", "실시간 혼잡도 정보를 불러올 수 없습니다.")

        # 2. 날씨 정보 추출
        weather_stts = city_data.get("WEATHER_STTS", [{}])[0]
        temp = weather_stts.get("TEMP", "-")
        pm10 = weather_stts.get("PM10_INDEX", "보통")
        weather_msg = weather_stts.get("PCP_MSG", "맑음")
        
        # 날씨 메시지가 비어있을 경우 기본값 설정
        if not weather_msg or str(weather_msg).strip() == "":
            weather_msg = "맑음"

        return {
            "congestion": congestion,
            "recommend_message": congest_msg,
            "weather": {
                "temp": temp,
                "msg": weather_msg,
                "pm10": pm10
            }
        }
    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        return {
            "congestion": "연결 실패",
            "recommend_message": "데이터를 불러오는 중 오류가 발생했습니다.",
            "weather": None
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)