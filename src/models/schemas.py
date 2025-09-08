"""
Pydantic models for API request and response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article model"""
    title: str = Field(..., description="Article title")
    link: str = Field(..., description="Article URL")
    snippet: str = Field(..., description="Article snippet/summary")


class Article(ArticleBase):
    """Article model with additional fields"""
    id: Optional[int] = Field(None, description="Article ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class NewsSearchRequest(BaseModel):
    """Request model for news search"""
    query: str = Field(..., description="Search query", min_length=1, max_length=200)
    format: Optional[str] = Field("json", description="Output format", pattern="^(json|csv)$")
    max_results: Optional[int] = Field(50, description="Maximum number of results", ge=1, le=100)


class NewsSearchResponse(BaseModel):
    """Response model for news search"""
    query: str = Field(..., description="Search query used")
    total_results: int = Field(..., description="Total number of articles found")
    articles: List[Article] = Field(..., description="List of articles")
    format: str = Field(..., description="Output format")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
