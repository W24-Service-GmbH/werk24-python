from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

__all__ = [
    "SystemStatus",
    "SystemStatusComponent",
    "SystemStatusIncident",
    "SystemStatusMaintenance",
]


class SystemStatusIncident(BaseModel):
    """Represents an incident currently affecting the platform."""

    name: str
    status: str
    shortlink: Optional[str] = None


class SystemStatusMaintenance(BaseModel):
    """Scheduled maintenance information."""

    name: str
    status: str
    scheduled_for: Optional[datetime] = None


class SystemStatusComponent(BaseModel):
    """Status information for a specific API component."""

    id: str
    name: str
    status: str
    updated_at: Optional[datetime] = None


class SystemStatus(BaseModel):
    """Overall system status returned by the status endpoint."""

    page: Optional[str] = None
    status_indicator: str
    status_description: Optional[str] = None
    incidents: List[SystemStatusIncident] = Field(default_factory=list)
    scheduled_maintenances: List[SystemStatusMaintenance] = Field(
        default_factory=list
    )
    components: List[SystemStatusComponent] = Field(default_factory=list)
