import streamlit as st
import feedparser
import schedule
import time
from openai import OpenAI
import threading

# OpenAI API 키 설정
openai_api_key = st.secrets["openai"]["api_key"]

# 세션 상태 초기화
if 'news_sites' not in st.session_state:
    st.session_state.news_sites = []
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'summaries' not in st.session_state:
    st.session_state.summaries = []

# 뉴스 사이트 추가 함수
def add_news_site():
    site = st.session_state.new_site
    if site and site not in st.session_state.news_sites:
        st.session_state.news_sites.append(site)
    st.session_state.new_site = ""

# 관심 주제 추가 함수
def add_topic():
    topic = st.session_state.new_topic
    if topic and topic not in st.session_state.topics:
        st.session_state.topics.append(topic)
    st.session_state.new_topic = ""

# 뉴스 요약 함수
def summarize_news(title, content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
            {"role": "user", "content": f"Summarize this news article in Korean:\nTitle: {title}\nContent: {content}"}
        ]
    )
    return response.choices[0].message.content

# 뉴스 수집 및 요약 함수
def fetch_and_summarize_news():
    for site in st.session_state.news_sites:
        feed = feedparser.parse(site)
        for entry in feed.entries[:5]:  # 각 사이트에서 최근 5개의 뉴스만 가져옴
            title = entry.title
            content = entry.summary if 'summary' in entry else entry.description if 'description' in entry else ""
            
            # 관심 주제와 일치하는 뉴스만 요약
            if any(topic.lower() in title.lower() or topic.lower() in content.lower() for topic in st.session_state.topics):
                summary = summarize_news(title, content)
                st.session_state.summaries.append({"title": title, "summary": summary})

# 백그라운드에서 주기적으로 뉴스 수집 및 요약
def news_update_job():
    while True:
        fetch_and_summarize_news()
        time.sleep(3600)  # 1시간마다 업데이트

# 백그라운드 작업 시작
threading.Thread(target=news_update_job, daemon=True).start()

# Streamlit 앱 UI
st.title("실시간 뉴스 요약 앱")

# 뉴스 사이트 등록
st.subheader("뉴스 사이트 등록")
st.text_input("뉴스 사이트 RSS 주소를 입력하세요", key="new_site", on_change=add_news_site)
st.write("등록된 뉴스 사이트:", st.session_state.news_sites)

# 관심 주제 등
