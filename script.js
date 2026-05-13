let locations = [];
const markerMap = {};

const seoulBounds = [
    [37.42, 126.75], // 남서단 (인천/시흥 경계 부근)
    [37.71, 127.20]  // 북동단 (의정부/남양주 경계 부근)
];

const map = L.map('map', { 
    zoomControl: false, 
    tap: false,
    maxBounds: seoulBounds,         // 영역 고정
    maxBoundsViscosity: 1.0,        // 튕겨나오는 강도
    minZoom: 13,                    // 최소 축소 레벨
    maxZoom: 18                     // 최대 확대 레벨
}).setView([37.5665, 126.9780], 12);

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    bounds: seoulBounds
}).addTo(map);

setTimeout(() => { map.invalidateSize(); }, 500);

// 2. 서비스 시작
async function startService() {
    try {
        const response = await fetch('./locations.json');
        locations = await response.json();
        initMarkers();
    } catch (error) {
        console.error("장소 데이터를 불러올 수 없습니다.");
    }
}

// 3. 마커 생성 및 실시간 색상 반영
function initMarkers() {
    locations.forEach(async (loc) => {
        // 기본 마커 디자인 (초기값은 회색)
        const mbtiIcon = L.divIcon({
            className: 'custom-mbti-icon',
            html: `<div class="mbti-marker-card" style="border-left: 5px solid #ccc;">
                    <span class="mbti-name" style="font-size: 16px; font-weight: 800; display: block;">${loc.name}</span>
                    <span class="mbti-type" style="font-size: 11px; color: #666;">${loc.mbti}</span>
                   </div>`,
            iconSize: [95, 65], iconAnchor: [47, 32]
        });

        const marker = L.marker([loc.lat, loc.lng], { icon: mbtiIcon }).addTo(map);
        markerMap[loc.official] = marker;

        // 🚀 마커 생성 즉시 실시간 데이터 가져와서 색상 변경
        try {
            const res = await fetch(`https://seoul-vibe-api.onrender.com/api/recommend/${loc.official}`);
            const data = await res.json();
            
            // 오류 방지: 마커가 화면에 그려지기 전에 찾으려고 하면 멈추는 현상 방지
            const el = marker.getElement();
            if (el) {
                const card = el.querySelector('.mbti-marker-card');
                let color = "#ccc"; 
                if (data.congestion === "여유") color = "#27ae60";      // 초록
                else if (data.congestion === "보통") color = "#f39c12"; // 주황
                else if (data.congestion === "약간 붐빔" || data.congestion === "붐빔") color = "#e74c3c"; // 빨강
    
                card.style.borderLeft = `6px solid ${color}`;
            }
        } catch (e) {
            console.log(`${loc.name} 데이터 업데이트 대기 중...`);
        }

        // 마커 클릭 이벤트
        marker.on('click', async () => {
            // 패널 기본정보 즉시 업데이트
            document.getElementById('panel-title').innerText = loc.name;
            document.getElementById('panel-mbti').innerText = loc.mbti;
            document.getElementById('panel-desc').innerText = loc.desc;
            
            const pLevel = document.getElementById('panel-level');
            if(pLevel) pLevel.innerText = "조회 중...";
            
            map.flyTo([loc.lat, loc.lng], 15);

            // 실시간 데이터로 패널 상세 업데이트
            try {
                const res = await fetch(`https://seoul-vibe-api.onrender.com/api/recommend/${loc.official}`);
                const data = await res.json();
                
                const levelEl = document.getElementById('panel-level');
                const cont = document.getElementById('congest-container');
                const msgEl = document.getElementById('panel-msg');

                if(cont) cont.classList.remove('low', 'medium', 'high');
                if(levelEl) levelEl.innerText = data.congestion;
                if(msgEl) msgEl.innerText = data.recommend_message;

                // 혼잡도 단계별 색상 적용
                if (cont) {
                    if (data.congestion === "여유") cont.classList.add('low');
                    else if (data.congestion === "보통") cont.classList.add('medium');
                    else cont.classList.add('high');
                }

                // 날씨 정보 적용 (요소가 없을 때 에러나는 것 방지)
                if (data.weather) {
                    const wTemp = document.getElementById('weather-temp');
                    const wMsg = document.getElementById('weather-msg');
                    const dStatus = document.getElementById('dust-status');
                    
                    if(wTemp) wTemp.innerText = `${data.weather.temp}°C`;
                    if(wMsg) wMsg.innerText = data.weather.msg;
                    if(dStatus) dStatus.innerText = data.weather.pm10;
                }

                // 🚀 AI 코스 생성 핵심 로직
                const aiBox = document.getElementById('ai-course-result');
                
                // 1. 만약 HTML에 박스가 없다면 크게 경고창을 띄웁니다!
                if (!aiBox) {
                    console.error("🚨 HTML 파일에 id가 'ai-course-result'인 태그가 없습니다!");
                    alert("앗! HTML에 AI를 띄울 박스가 없습니다. index.html 코드를 확인해주세요.");
                    return; // 더 이상 진행하지 않음
                }

                // 2. 박스가 있다면 정상 진행
                aiBox.innerHTML = "🤖 AI가 코스를 구성 중입니다..."; 
                
                try {
                    const aiRes = await fetch(`https://seoul-vibe-api.onrender.com/api/ai-course/${loc.official}`);
                    const aiData = await aiRes.json();
                    
                    aiBox.innerHTML = ""; 

                    // AI가 제대로 된 리스트(courses)를 주었을 때만 실행
                    if (aiData.courses && aiData.courses.length > 0) {
                        aiData.courses.forEach((item, index) => {
                            const section = document.createElement('div');
                            section.className = 'course-item'; 
                            section.innerHTML = `
                                <div class="course-header">
                                    <span class="course-number">${index + 1}</span>
                                    <span class="course-icon">${item.icon}</span>
                                    <span class="course-place">${item.place}</span>
                                </div>
                                <div class="course-reason">${item.reason}</div>
                            `;
                            aiBox.appendChild(section);
                        });
                    } else {
                        // 서버가 에러를 보냈거나 데이터가 비어있을 때
                        aiBox.innerHTML = "❌ AI 응답 형식이 올바르지 않습니다.";
                        console.error("서버에서 받은 AI 데이터 이상:", aiData);
                    }
                } catch (err) {
                    // 통신 자체가 실패했을 때
                    console.error("AI 통신 중 오류 발생:", err);
                    aiBox.innerHTML = "❌ 서버와 통신할 수 없습니다.";
                }
                
            } catch (err) {
                // 혼잡도/날씨 업데이트 중 오류 발생 시
                console.error("기본 정보 업데이트 오류:", err);
                const levelEl = document.getElementById('panel-level');
                if(levelEl) levelEl.innerText = "오류 발생";
            }
        });
    });
}

// 4. 검색창 엔터 키 이벤트
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const val = e.target.value.trim();
        const found = locations.find(l => l.name.includes(val) || l.official.includes(val));
        if (found) markerMap[found.official].fire('click');
        else alert("검색 결과가 없습니다.");
    }
});

// 5. 내 위치 버튼 클릭 이벤트
document.getElementById('geo-btn').addEventListener('click', () => {
    if (!navigator.geolocation) return alert("위치 정보를 지원하지 않습니다.");
    
    navigator.geolocation.getCurrentPosition((pos) => {
        let closest = null, minD = Infinity;
        locations.forEach(l => {
            const d = Math.hypot(l.lat - pos.coords.latitude, l.lng - pos.coords.longitude);
            if (d < minD) { minD = d; closest = l; }
        });
        if (closest) markerMap[closest.official].fire('click');
    });
});

startService();