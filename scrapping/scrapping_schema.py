from pydantic import BaseModel


# Pydantic model for request validation
class CrawlRequest(BaseModel):
    url: str
