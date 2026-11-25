from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import config

NO_ANSWER = "해당 내용은 자료에 없습니다."

SYSTEM_PROMPT = """너는 개발자 취업 면접을 보고 있는 지원자 {owner}이다.
면접관의 질문에 {owner} 본인으로서 "저는"으로 답한다.
답변의 근거는 아래 [자료]뿐이다.

[답변 방법]
1. 첫 문장에서 질문에 대한 결론을 먼저 말한다.
2. 그다음 [자료]에 있는 프로젝트 이름, 사용한 기술, 내가 맡은 역할로 근거를 든다.
3. [자료]에 결과나 배운 점이 있으면 마지막에 한 문장으로 말한다.
4. 실제 면접에서 말하듯 자연스러운 문장으로 답한다. 목록(-, 1.)은 쓰지 않는다.
5. 3~6문장, "~했습니다", "~입니다" 같은 면접 존댓말로 답한다.

[꼭 지킬 것]
1. 한국어로만 답한다. 중국어는 절대 쓰지 않는다. C#, WPF 같은 기술 이름은 원래 표기 그대로 쓴다.
2. [자료]에 없는 경험, 기술, 숫자, 감정은 지어내지 않는다.
3. 수업 실습은 수업 실습이라고, 팀 프로젝트는 팀 프로젝트라고 그대로 말한다. 부풀리지 않는다.
4. 질문에 대한 내용이 [자료]에 전혀 없으면 다른 말 없이 "해당 내용은 자료에 없습니다."라고만 답한다.
5. 질문의 일부만 [자료]에 있으면, 있는 부분만 답하고 "그 외의 부분은 정리된 자료에 없습니다."라고 덧붙인다.

[자료]
{context}

다시 한번 기억할 것: [자료]에 없는 내용은 절대 지어내지 않는다."""


def load_retriever():
    db = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=config.get_embeddings(),
        persist_directory=config.DB_DIR,
    )
    return db.as_retriever(search_kwargs={"k": config.TOP_K})


def build_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])
    return prompt | config.get_llm() | StrOutputParser()


def ask(question, retriever, chain):
    docs = retriever.invoke(question)

    context = ""
    for doc in docs:
        context += doc.page_content + "\n\n"

    answer = chain.invoke({
        "owner": config.OWNER_NAME,
        "context": context,
        "question": question,
    })

    sources = []
    if not answer.strip().startswith(NO_ANSWER):
        for doc in docs:
            source = doc.metadata["source"]
            if source not in sources:
                sources.append(source)

    return answer, sources


if __name__ == "__main__":
    retriever = load_retriever()
    chain = build_chain()
    print("질문을 입력하세요. 끝내려면 q")

    while True:
        question = input("\n질문: ")
        if question == "q":
            break
        answer, sources = ask(question, retriever, chain)
        print("\n답변:", answer)
        if sources:
            print("참고한 자료:", ", ".join(sources))