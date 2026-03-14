from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str
    device_type: str = "unknown"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    status: str


class JobCreate(BaseModel):
    customer_name: str
    customer_phone: str = ""
    customer_email: str = ""
    job_description: str = ""
    plumber_name: str = ""


class JobResponse(BaseModel):
    session_id: str
    review_link: str


class SessionInfo(BaseModel):
    session_id: str
    customer_name: str
    status: str
    device_type: str
    created_at: str
    message_count: int


class AnalyticsResponse(BaseModel):
    reviews_today: int
    reviews_this_week: dict[str, int]
    total_sessions: int
    completion_rate: float
