from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from database.db_connect import get_session
from schemas import Report, ReportRead

router = APIRouter()

@router.get("/", response_model=List[ReportRead])
async def get_all_reports(session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all available reports.
    """
    result = await session.execute(select(Report).offset(skip).limit(limit).order_by(Report.created_at.desc()))
    reports = result.scalars().all()
    return reports

@router.get("/scan/{scan_id}", response_model=List[ReportRead])
async def get_reports_for_scan(scan_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve all reports associated with a specific scan ID.
    """
    result = await session.execute(select(Report).where(Report.scan_id == scan_id))
    reports = result.scalars().all()
    if not reports:
        raise HTTPException(status_code=404, detail=f"No reports found for scan ID: {scan_id}")
    return reports

@router.get("/{report_id}/download")
async def download_report(report_id: int, session: AsyncSession = Depends(get_session)):
    """
    Download a specific report by its database ID.
    """
    report = await session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    if report.report_type == 'pdf':
        media_type = 'application/pdf'
        filename = f"CyberSentinel_Report_{report.scan_id}.pdf"
    elif report.report_type == 'json':
        media_type = 'application/json'
        filename = f"CyberSentinel_Report_{report.scan_id}.json"
    else:
        # Should not happen, but as a fallback
        media_type = 'application/octet-stream'
        filename = f"CyberSentinel_Report_{report.scan_id}.dat"
        
    return Response(
        content=report.content_blob,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
