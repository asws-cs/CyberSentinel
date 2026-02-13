from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.helpers import to_json # Import to_json

# Shared properties
class ScanBase(SQLModel):
    target: str = Field(index=True)
    scan_mode: str
    scan_depth: str
    status: str = Field(default="pending", index=True)

# Database model
class Scan(ScanBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    scan_id: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    
    results: List["ScanResult"] = Relationship(back_populates="scan")

# Properties to receive via API on creation
class ScanCreate(ScanBase):
    aggressive: bool = False
    tools: Optional[List[str]] = None

# Properties to return via API
class ScanRead(ScanBase):
    id: int
    scan_id: str
    created_at: datetime
    finished_at: Optional[datetime] = None

# Using JSON for flexible findings
class ScanResultBase(SQLModel):
    tool_name: str
    findings_json: str = Field(sa_column_kwargs={"name": "findings"})

    @property
    def findings(self) -> Dict[str, Any]:
        # Still use json.loads for reading, as it expects a string
        return json.loads(self.findings_json)

    @findings.setter
    def findings(self, value: Dict[str, Any]):
        self.findings_json = to_json(value)

class ScanResult(ScanResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    scan_id: str = Field(foreign_key="scan.scan_id")
    scan: Scan = Relationship(back_populates="results")
    
class ScanResultCreate(ScanResultBase):
    pass

class ScanResultRead(ScanResultBase):
    id: int

class ScanReadWithResults(ScanRead):
    results: List[ScanResultRead] = []

class ReportBase(SQLModel):
    scan_id: str = Field(foreign_key="scan.scan_id", index=True)
    report_type: str # 'json' or 'pdf'
    risk_score: int
    severity: str

class Report(ReportBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    content_blob: bytes = Field(sa_column_kwargs={"name": "content"})

class ReportRead(ReportBase):
    id: int
    created_at: datetime
