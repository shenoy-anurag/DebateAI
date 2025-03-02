import os

from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


def process_files():
    docs = []
    for file_name in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file_name)

        try:
            print(f"🔍 Processing file: {file_path}")

            if file_name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_name.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                print(f"⚠️ Skipping unsupported file: {file_name}")
                continue

            loaded_docs = loader.load()
            print(f"✅ Successfully loaded {file_name}")

            docs.extend(loaded_docs)

        except Exception as e:
            print(f"❌ Error loading {file_name}: {str(e)}")

    if not docs:
        print("❌ No valid documents found!")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(texts, OpenAIEmbeddings())
    vectorstore.save_local(VECTORSTORE_DIR)

    print("✅ Knowledge base updated successfully!")