import os
import uuid
import logging
from dotenv import load_dotenv
from typing import List

from pinecone import Pinecone
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
# from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from scrapping.crawler import WebCrawler
# from crawler import WebCrawler


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PopulateVectorDB:
    def __init__(self):
        self.crawler = WebCrawler()
        self.embeddings = FastEmbedEmbeddings(cache_dir="embed_model")
        self.text_splitter = self.create_text_splitter()
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY', ""))
        self.index = self.pc.Index(os.getenv('PINECONE_INDEX_NAME', "webmind"))
        
    def get_data(self, url: str) -> List[str]:
        """Fetch web data using the crawler."""
        logger.info(f"Fetching data from {url}...")
        crawl_status = self.crawler.get_web_data(url)

        if crawl_status and crawl_status.get('status') == 'completed':
            extracted_info = [entry["markdown"] for entry in crawl_status.get("data", []) if "markdown" in entry]
            logger.info(f"Extracted {len(extracted_info)} documents.")
            return extracted_info
        else:
            logger.warning(f"Failed to crawl {url}.")
            return []

    def create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create and return a text splitter object."""
        logger.info("Initializing text splitter...")
        return RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            separators=[
                "\n\n", "\n", " ", ".", ",", "\u200b",  # Zero-width space
                "\uff0c", "\u3001", "\uff0e", "\u3002", ""  # Fullwidth & Ideographic punctuation
            ],
        )

    def create_embeddings(self, texts: List[str]) -> bool:
        """Generate embeddings for text chunks and insert into Pinecone."""
        if not texts:
            logger.warning("No text data provided for embeddings.")
            return False

        try:
            logger.info("Generating embeddings...")
            vectors = []

            for text in texts:
                chunks = self.text_splitter.create_documents([text])  # Fixed incorrect method call

                embeddings = self.embeddings.embed_documents([chunk.page_content for chunk in chunks])  # Fixed method call
                index = 0
                for chunk, embedding in zip(chunks, embeddings):
                    logger.info(f"chunk # {str(index)} processing.....")
                    vectors.append((str(uuid.uuid4()), embedding, {"text": chunk.page_content}))

            if vectors:
                self.index.upsert(vectors, namespace="zain")
                logger.info(f"Inserted {len(vectors)} vectors into Pinecone.")
            return True
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return False
    def get_retrieved_data(self, query: str, namespace : str = "zain") -> List[dict]:
        """Retrieve data from Pinecone based on a query."""
        try:
            logger.info(f"Retrieving data for query: {query}")
            query_vector = self.embeddings.embed_query(query)
            response = self.index.query(vector=query_vector, top_k=3, include_metadata=True, namespace=namespace)
            results = [{"id": match.id, "score": match.score, "text": match.metadata["text"]} for match in response.matches]
            logger.info(f"Retrieved {len(results)} results.")
            return results
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            return []   
if __name__ == "__main__":
    pop = PopulateVectorDB()
    data = pop.get_data("https://heallabsonline.com")
    pop.create_embeddings(data)
