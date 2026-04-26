async function checkCongestion() {
    const area = document.getElementById('areaSelect').value;
    const resultBox = document.getElementById('result-box');
    
    // 로딩 표시
    resultBox.style.display = 'block';
    document.getElementById('res-area').innerText = area;
    document.getElementById('res-level').innerText = "조회 중...";
    document.getElementById('res-msg').innerText = "데이터를 분석하고 있습니다 ⏳";
    document.getElementById('res-level').style.color = "#333";

    try {
        // 🚨 로컬 파이썬 서버 주소로 직접 데이터 요청 (배포 전 상태)
        const response = await fetch(`http://127.0.0.1:8000/api/recommend/${area}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();

        // 화면 업데이트
        document.getElementById('res-icon').innerText = data.status_icon;
        document.getElementById('res-level').innerText = data.congestion;
        
        if(data.congestion.includes("붐빔") || data.congestion.includes("High")) {
            document.getElementById('res-level').style.color = "#e74c3c"; 
        } else {
            document.getElementById('res-level').style.color = "#27ae60"; 
        }

        document.getElementById('res-msg').innerHTML = data.recommend_message;
        
    } catch (error) {
        document.getElementById('res-level').innerText = "오류 발생";
        document.getElementById('res-level').style.color = "#e74c3c";
        document.getElementById('res-msg').innerText = "서버와 연결할 수 없습니다. 파이썬 백엔드 서버(main.py)가 실행 중인지 확인해주세요.";
        console.error("API 통신 에러:", error);
    }
}