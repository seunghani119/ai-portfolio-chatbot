import os
import shutil
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import config


def load_documents():
    docs = []
    for root, dirs, files in os.walk(config.DATA_DIR):
        for file_name in files:
            if not file_name.endswith(".md"):
                continue

            path = os.path.join(root, file_name)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            title = file_name
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:]
                    break

            doc = Document(page_content=text, metadata={"source": file_name, "title": title})
            docs.append(doc)
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n## ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.page_content = "[" + chunk.metadata["title"] + "]\n" + chunk.page_content
    return chunks


def main():
    docs = load_documents()
    print("문서 개수:", len(docs))

    chunks = split_documents(docs)
    print("조각 개수:", len(chunks))

    if os.path.exists(config.DB_DIR):
        shutil.rmtree(config.DB_DIR)

    Chroma.from_documents(
        documents=chunks,
        embedding=config.get_embeddings(),
        collection_name=config.COLLECTION_NAME,
        persist_directory=config.DB_DIR,
    )
    print("벡터 DB 저장 완료")


if __name__ == "__main__":
    main()