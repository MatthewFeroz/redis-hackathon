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
    customer_address: str = ""
    customer_zip: str = ""
    referral_source: str = ""
    job_description: str = ""
    job_type: str = ""
    job_total: str = ""
    job_date: str = ""
    plumber_name: str = ""
    is_repeat_customer: bool = False
    follow_up_notes: str = ""


class JobResponse(BaseModel):
    session_id: str
    review_link: str
    sms_sent: bool = False
    sms_error: str | None = None


class SessionInfo(BaseModel):
    session_id: str
    organization_id: str | None = None
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


class CustomerMapPoint(BaseModel):
    session_id: str
    organization_id: str | None = None
    customer_name: str
    customer_address: str = ""
    customer_zip: str = ""
    status: str
    latitude: float
    longitude: float
    geocode_source: str = ""


class OrganizationSummary(BaseModel):
    id: str
    name: str
    slug: str
    role: str


class MeResponse(BaseModel):
    user_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: str
    platform_role: str | None = None
    is_superadmin: bool = False
    organization: OrganizationSummary | None = None
    organizations: list[OrganizationSummary] = []


class OrganizationSwitchRequest(BaseModel):
    organization_id: str
