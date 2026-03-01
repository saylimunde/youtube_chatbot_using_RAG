import streamlit as st
from rag_pipeline import generate_answer

st.set_page_config(page_title="YouTube RAG Chatbot")
st.title("🎥 YouTube RAG Chatbot")
st.write("Ask questions about any YouTube video using Retrieval-Augmented Generation.")

video_id = st.text_input("Enter YouTube Video ID")
question = st.text_input("Ask your question")

if st.button("Generate Answer"):
    if video_id and question:
        try:
            with st.spinner("Generating answer..."):
                answer = generate_answer(video_id, question)
                st.success("Answer Generated")
                st.write(answer)
        except Exception as e:
                st.error("Something went wrong. Please check the video ID.")
      
    else:
        st.warning("Please enter both fields.")