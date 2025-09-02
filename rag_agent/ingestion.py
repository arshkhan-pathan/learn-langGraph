from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

urls = [
    "https://www.evoindia.com/blog/adils-blog-f1-movie-review-587008",
    "https://www.psychologytoday.com/us/blog/relationship-building/202506/how-the-f1-movie-changes-how-we-see-success",
    "https://www.kymillman.com/blog/what-did-the-f1-movie-miss/?srsltid=AfmBOopA6r1G5MMnK3YDNoFZbcerRD4xWSl3U0Pq3UGJRuG3eZl3gc4E",
]

# docs = [WebBaseLoader(url).load() for url in urls]
# docs_list = [item for sublist in docs for item in sublist]
#
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     chunk_size=250, chunk_overlap=0
# )
# doc_splits = text_splitter.split_documents(docs_list)
#
google_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"  # Required parameter
)
#
# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=google_embeddings,  # Changed here
#     persist_directory="./.chroma",
# )

retriever = Chroma(
    collection_name="rag-chroma",
    persist_directory="/home/arshkha/Documents/learn/learn-langgraph/rag_agent/.chroma",
    embedding_function=google_embeddings,  # Changed here
).as_retriever()

# relevant_docs = retriever.invoke("Tell me about the F1 Movie")
# print("relevant_docs", relevant_docs)