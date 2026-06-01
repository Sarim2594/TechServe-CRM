from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["manager", "agent"]
TicketStatus = Literal["Open", "In Progress", "Resolved", "Closed"]
TicketPriority = Literal["Low", "Medium", "High", "Critical"]


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class CustomerBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    assigned_agent_id: int | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    assigned_agent_id: int | None = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    assigned_agent: UserSummary | None = None


class CustomerTicketSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    category: str | None = None
    created_at: datetime


class CustomerDetailResponse(CustomerResponse):
    ticket_history: list[CustomerTicketSummary] = Field(default_factory=list)


class TicketBase(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str = Field(min_length=5)
    status: TicketStatus = "Open"
    priority: TicketPriority = "Medium"
    category: str | None = Field(default=None, max_length=80)
    customer_id: int
    assigned_agent_id: int | None = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=240)
    description: str | None = Field(default=None, min_length=5)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    category: str | None = Field(default=None, max_length=80)
    customer_id: int | None = None
    assigned_agent_id: int | None = None


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    ai_category: str | None = None
    ai_sentiment: str | None = None
    ai_summary: str | None = None
    customer: CustomerResponse
    assigned_agent: UserSummary | None = None


class TicketOut(TicketResponse):
    pass


class TicketCommentCreate(BaseModel):
    message: str = Field(min_length=1)
    is_internal: bool = True


class TicketCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    agent_id: int
    message: str
    is_internal: bool
    created_at: datetime
    agent: UserSummary


class TicketCommentOut(TicketCommentResponse):
    pass


class TicketActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    actor_id: int
    action: str
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime
    actor: UserSummary


class TicketActivityOut(TicketActivityResponse):
    pass


class TicketDetailOut(TicketOut):
    comments: list[TicketCommentOut] = Field(default_factory=list)
    activity_log: list[TicketActivityOut] = Field(default_factory=list)


class TicketAIAnalysis(BaseModel):
    ai_category: str
    ai_sentiment: str
    escalation_recommended: bool


class TicketAISuggestion(BaseModel):
    suggestion: str


class TicketAISummary(BaseModel):
    summary: str


class NotificationLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    platform: str
    message: str
    status: str
    sent_at: datetime


class DashboardRecentTicket(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    category: str
    customer_name: str
    assigned_agent_name: str | None = None
    created_at: datetime


class AgentWorkload(BaseModel):
    agent_id: int
    agent_name: str
    total_assigned_tickets: int
    open_assigned_tickets: int
    in_progress_assigned_tickets: int
    resolved_assigned_tickets: int
    critical_assigned_tickets: int


class DashboardStats(BaseModel):
    total_customers: int
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    resolved_today: int
    critical_tickets: int
    high_priority_tickets: int
    tickets_by_status: dict[str, int]
    tickets_by_priority: dict[str, int]
    tickets_by_category: dict[str, int]
    recent_tickets: list[DashboardRecentTicket]
    agent_workloads: list[AgentWorkload]


class RecentResolvedTicket(BaseModel):
    id: int
    title: str
    category: str
    priority: TicketPriority
    customer_name: str
    assigned_agent_name: str | None = None
    resolved_at: datetime


class ReportSummary(BaseModel):
    total_tickets: int
    total_customers: int
    ticket_count_by_category: dict[str, int]
    ticket_count_by_status: dict[str, int]
    ticket_count_by_priority: dict[str, int]
    ticket_count_by_agent: dict[str, int]
    resolved_tickets: int
    average_resolution_time_hours: float | None
    critical_tickets: int
    recent_resolved_tickets: list[RecentResolvedTicket]


class TicketFilters(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    agent_id: int | None = None
    customer_id: int | None = None
    search: str | None = None
    date_from: date | None = None
    date_to: date | None = None
