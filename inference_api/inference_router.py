import os
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from inference_api.inference_schema import InferenceRequest
from inference_api.llm_inference import LLMInference

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API Router
inference_router = APIRouter(prefix="/api", tags=["LLM Inference"])

@inference_router.post("/echo")
async def echo(request: InferenceRequest):
    """
    Echoes back the received request data.
    This is a placeholder endpoint for testing purposes.
    """
    logger.info(f"Received echo request with query: {request.query}---{request.api_key}, {request.chat_history}")
    return "You said " + request.query

@inference_router.post("/inference")
async def inference(request: InferenceRequest):
    """
    Processes inference requests for an LLM model.
    Validates the API key and returns the response from the LLM model.
    """
    try:
        logger.info(f"Received inference request with query: {request.query}---{request.api_key}")

        # Validate API Key
        if request.api_key != os.getenv('WEBMIND_API_KEY'):
            raise HTTPException(status_code=401, detail="Invalid API Key")

        # Initialize LLM Inference
        llm_inference = LLMInference(api_key=request.api_key)
        response = llm_inference.get_response(request.query, request.chat_history)

        if not response:
            raise HTTPException(status_code=400, detail="Failed to generate response")

        return response
    except Exception as e:
        logger.error(f"Error in inference: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
