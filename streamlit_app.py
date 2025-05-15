import streamlit as st
import requests
import json
from datetime import datetime

# Streamlit 앱 제목 설정
st.title("네이버 뉴스 검색")

# 화면에서 Client ID와 Client Secret 입력 받기
CLIENT_ID = st.text_input("NAVER Client ID 입력:")
CLIENT_SECRET = st.text_input("NAVER Client Secret 입력:", type="password")

# 검색어 입력 받기
keyword = st.text_input("검색어를 입력하세요:", "제주 감귤")

# 뉴스 개수 선택
display = st.slider("가져올 뉴스 개수:", 5, 20, 10)

if st.button("검색"):
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error("NAVER Client ID와 Client Secret을 모두 입력해주세요.")
    else:
        # API 엔드포인트 설정
        url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display={display}&sort=date"

        # HTTP 요청 헤더 설정
        headers = {
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET
        }

        # API 요청 보내기
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            news_items = data['items']
            st.subheader(f"'{keyword}' 관련 최신 뉴스:")
            for item in news_items:
                title = item['title'].replace("<b>", "").replace("</b>", "")  # HTML 태그 제거
                link = item['link']
                date_str = item['pubDate']
                date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"- **{title}**: [{link}]({link}) ({formatted_date})")
        else:
            st.error(f"API 요청 실패: {response.status_code}")
            st.error(response.text)
