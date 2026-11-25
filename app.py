import os
import streamlit as st
import config
import rag

st.set_page_config(page_title="AI 포트폴리오 챗봇", page_icon="🤖")
st.title("🤖 " + config.OWNER_NAME + " AI 포트폴리오 챗봇")
st.caption("이 답변은 " + config.OWNER_NAME + "의 포트폴리오 자료를 바탕으로 AI가 만든 답변입니다. 면접관이 된 것처럼 질문해 보세요.")

if not os.path.exists(config.DB_DIR):
    st.error("벡터 DB가 없습니다. 터미널에서 python ingest.py를 먼저 실행하세요.")
    st.stop()


@st.cache_resource
def load_bot():
    retriever = rag.load_retriever()
    chain = rag.build_chain()
    return retriever, chain


retriever, chain = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["sources"]:
            st.caption("참고한 자료: " + ", ".join(msg["sources"]))

questions = ["어떤 프로젝트를 해봤나요?", "팀에서 어떤 역할을 맡았나요?", "가장 자신 있는 기술은 무엇인가요?"]
clicked = None
cols = st.columns(3)
for i in range(3):
    if cols[i].button(questions[i]):
        clicked = questions[i]

question = st.chat_input("면접 질문을 입력하세요")
if clicked:
    question = clicked

if question:
    st.session_state.messages.append({"role": "user", "content": question, "sources": []})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("자료를 찾는 중..."):
            answer, sources = rag.ask(question, retriever, chain)
        st.markdown(answer)
        if sources:
            st.caption("참고한 자료: " + ", ".join(sources))

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})