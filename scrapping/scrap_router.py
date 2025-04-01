import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Header
import logging

from scrapping.scrapping_schema import CrawlRequest  # Import your Pydantic model
from scrapping.populate_vectordb import PopulateVectorDB  # Import your class


load_dotenv()
# Load environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api", tags=["Web Crawling"])


# Dependency injection (for future enhancements)
def get_vector_db():
    return PopulateVectorDB()

@router.post("/crawl")
async def crawl_website(
    request: CrawlRequest,
    vector_db: PopulateVectorDB = Depends(get_vector_db),
    api_key: str = Header(None),  # API key is now taken from request headers
):
    """
    Takes a URL and an API key from the request headers, fetches data using `populate_vectordb`,
    generates embeddings, and stores them in Pinecone.
    """
    logger.info(f"Received crawl request for URL: {request.url}")

    # Validate API Key (Modify this logic as needed)
    if api_key != os.getenv('WEBMIND_API_KEY'):  
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Fetch website data
    extracted_data = vector_db.get_data(request.url)
    if not extracted_data:
        raise HTTPException(status_code=400, detail="Failed to fetch data from URL")

    # Create embeddings
    success = vector_db.create_embeddings(extracted_data)
    if not success:
        raise HTTPException(status_code=500, detail="Embedding generation failed")

    return {"message": "Data successfully crawled and stored", "url": request.url, "status": "200"}
