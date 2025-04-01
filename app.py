from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure correct import paths
from scrapping.scrap_router import router  # Import the API router
from inference_api.inference_router import inference_router  # Ensure this module exists

# FastAPI app instance
app = FastAPI(title="Web Mind")

# CORS middleware (allows frontend requests from different origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include routers
app.include_router(inference_router)  # Ensure inference_router is correctly imported
app.include_router(router)  # Include scrap_router

# Run using: uvicorn filename:app --reload
if __name__=="__main__":
    import uvicorn
    uvicorn.run("app:app")