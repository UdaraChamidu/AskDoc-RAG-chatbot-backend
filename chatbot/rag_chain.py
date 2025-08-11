from .config import GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

import os

# LLM and Embeddings 
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,
    google_api_key=GOOGLE_API_KEY
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

#Prompt Template 
system_prompt = (
    "You are an intelligent chatbot. Use the following context to answer the question. "
    "If you don't know the answer, just say that you don't know.\n\n{context}"
    "Your name is AskDoc and you are a helpful assistant for answering questions based on the provided PDF documents.\n\n"
    "You must give more priority to the context provided in the PDF documents than to your own knowledge.\n\n"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

#Chat History Store 
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

#Dynamic RAG Chain Builder
loaded_chains = {}

def get_rag_chain(file_path):
    if file_path in loaded_chains:
        print(f"[DEBUG] Using cached chain for {file_path}")
        return loaded_chains[file_path]

    print(f"[DEBUG] Loading PDF from: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print(f"[DEBUG] Loaded {len(docs)} pages")

    if len(docs) == 0:
        print("[WARNING] No documents loaded from PDF!")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    print(f"[DEBUG] Created {len(splits)} chunks from PDF")

    vector_store = FAISS.from_documents(splits, embedding=embedding_model)
    retriever = vector_store.as_retriever()

    qa_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    loaded_chains[file_path] = conversational_rag_chain
    print(f"[DEBUG] Created and cached RAG chain for {file_path}")
    return conversational_rag_chain


#Unified ask function
def ask_question(question: str, file_path: str, session_id: str = "default"):
    chain = get_rag_chain(file_path)
    response = chain.invoke(
        {"input": question},
        config={"configurable": {"session_id": session_id}}
    )
    print(f"[DEBUG] Response answer: {response['answer']}")
    return response["answer"]
