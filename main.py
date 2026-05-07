import os
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🚀 Render에 등록한 환경 변수(API 키)를 파이썬이 읽어오도록 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

# 프론트엔드와 통신을 위한 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 본인의 API 키를 입력하세요!
SEOUL_API_KEY = "4c4663594b3036793731476d445950"
GEMINI_API_KEY = "AIzaSyBoLQF7HEj0kE8230uLXs3iNbtQPSDfysM"

@app.get("/")
def read_root():
    return {"message": "서예준 님의 AI 데이트 추천 서버가 실행 중입니다! 🚀"}

# [기능 1] 실시간 혼잡도 및 날씨 정보 가져오기
@app.get("/api/recommend/{area_name}")
async def get_live_data(area_name: str):
    try:
        url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/citydata/1/5/{area_name}"
        response = requests.get(url, timeout=30)
        data = response.json()
        city_data = data.get("CITYDATA", {})
        
        live_ppltn = city_data.get("LIVE_PPLTN_STTS", [{}])[0]
        weather_stts = city_data.get("WEATHER_STTS", [{}])[0]

        return {
            "congestion": live_ppltn.get("AREA_CONGEST_LVL", "정보 없음"),
            "recommend_message": live_ppltn.get("AREA_CONGEST_MSG", "-"),
            "weather": {
                "temp": weather_stts.get("TEMP", "-"),
                "msg": weather_stts.get("PCP_MSG", "맑음"),
                "pm10": weather_stts.get("PM10_INDEX", "보통")
            }
        }
    except Exception as e:
        return {"congestion": "오류", "recommend_message": "데이터 로드 실패", "weather": None}


# 🚀 [기능 2] 제미나이 AI 데이트 코스 추천 (가볍고 빠른 직통 방식!)
@app.get("/api/ai-course/{area_name}")
async def get_ai_course(area_name: str):
    # 변수를 미리 빈 값으로 준비해둡니다 (에러 방지)
    result_data = {} 
    
    try:
        # 1. 서울시 날씨 정보 가져오기
        url = f"http://openapi.seoul.go.kr:8088/{SEOUL_API_KEY}/json/citydata/1/5/{area_name}"
        res = requests.get(url, timeout=5).json()
        weather = res.get("CITYDATA", {}).get("WEATHER_STTS", [{}])[0]
        temp = weather.get("TEMP", "현재 기온")
        msg = weather.get("PCP_MSG", "맑음")

        # 2. 제미나이에게 "JSON 형식"으로 짧게 대답하라고 명령
        prompt = f"""
        너는 데이트 코스 전문가야. '{area_name}' 지역의 날씨({temp}도, {msg})에 맞는 코스 3곳을 추천해줘.
        반드시 아래의 JSON 형식을 지켜서 응답하고 다른 설명은 하지 마. 
        이유는 무조건 '한 문장'으로 아주 짧게 써줘.

        [
          {{"icon": "🍽️", "place": "식당이름", "reason": "이유"}},
          {{"icon": "☕", "place": "카페이름", "reason": "이유"}},
          {{"icon": "🎬", "place": "장소이름", "reason": "이유"}}
        ]
        """
        
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        # 3. 제미나이 호출 (시간을 30초로 넉넉히 줍니다)
        response = requests.post(gemini_url, json=payload, timeout=30)
        result_data = response.json() # 👈 여기서 데이터 할당!

        # 4. 데이터가 정상적으로 왔는지 확인 후 가공
        if "candidates" in result_data:
            raw_text = result_data["candidates"][0]["content"]["parts"][0]["text"]
            # AI가 준 텍스트에서 JSON 부분만 깨끗하게 추출
            clean_json = raw_text.replace('```json', '').replace('```', '').strip()
            course_list = json.loads(clean_json)
            
            return {"courses": course_list} # 🚀 자바스크립트로 리스트 전송!
        else:
            # 🚀 수정: "형식 오류"라고 퉁치지 말고, 제미나이가 보낸 원본을 그대로 보내라!
            return {"courses": [], "error": f"제미나이 원본 에러: {result_data}"}

    except Exception as e:
        return {"courses": [], "error": str(e)}