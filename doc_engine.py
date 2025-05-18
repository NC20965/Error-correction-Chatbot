import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

# Load OpenAI key and initialize LLM
llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

# Load documents from /data directory
documents = SimpleDirectoryReader("data").load_data()

# Build index
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine(llm=llm)

# Query function
def query_documents(user_query: str) -> str:
    return str(query_engine.query(user_query))
