import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

load_dotenv()


def get_transcript_text(video_id):
    api = YouTubeTranscriptApi()

    # Explicitly request Hindi auto-generated transcript
    transcript = api.fetch(video_id, languages=["hi"])

    # New versions return objects, not dictionaries
    text = " ".join([snippet.text for snippet in transcript])

    return text

def generate_answer(video_id, question):

    # 1️⃣ Fetch transcript
    text = get_transcript_text(video_id)

    # 2️⃣ Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = splitter.create_documents([text])

    # 3️⃣ Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

    # 4️⃣ Retrieve

    if "summarize" in question.lower():
        context_docs = vectorstore.similarity_search("", k=8)
    else:
        context_docs = retriever.invoke(question)

    context = " ".join(doc.page_content for doc in context_docs)
  


    # 5️⃣ LLM
    model = ChatGroq(model="llama-3.1-8b-instant")

    prompt = f"""
        You are an AI assistant.

        If the user asks for a summary:
        - Summarize the full context clearly.
        - Do not add external information.
       IMPORTANT INSTRUCTION:
        - You MUST respond only in English.
        - Even if the context is in Hindi, internally translate it and respond in English.
        - Do NOT write any Hindi words.
        - If the answer is generated in Hindi, translate it to English before responding.


        Context:
        {context}

        Question:
        {question}

        Answer:
    """

    response = model.invoke(prompt)

    return response.content