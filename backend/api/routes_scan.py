from fastapi import APIRouter, Depends, HTTPException, status, Body, Header
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional

from database.db_connect import get_session
from schemas import Scan, ScanCreate, ScanRead, ScanReadWithResults
from core.target_parser import Target, parse_target
from core.decision_engine import get_scan_pipeline
from core.queue_manager import get_queue
from security.legal_guard import LEGAL_DISCLAIMER
from tools.live_output import get_live_output_subscriber
from utils.logger import logger
import uuid
import json

router = APIRouter()

@router.post("/", response_model=ScanRead, status_code=status.HTTP_202_ACCEPTED)
async def start_new_scan(
    scan_in: ScanCreate = Body(...),
    x_legal_accepted: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Start a new scan for a given target.
    This endpoint is asynchronous and will return immediately.
    """
    if scan_in.scan_mode == 'offensive':
        if not x_legal_accepted or x_legal_accepted.lower() != "true":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Offensive scanning requires legal acceptance. "
                               "Set the 'X-Legal-Accepted' header to 'true'.",
                    "disclaimer": LEGAL_DISCLAIMER,
                },
            )

    try:
        scan_id = str(uuid.uuid4()) # scan_id is generated here
        target_obj = await parse_target(scan_in.target, scan_id)
        if not target_obj.ip_address and not target_obj.domain:
             raise HTTPException(status_code=400, detail="Invalid or unresolvable target.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    pipeline = get_scan_pipeline(
        scan_in.target, 
        scan_id, # Pass scan_id here
        scan_in.scan_mode, 
        scan_in.scan_depth,
        scan_in.aggressive,
        scan_in.tools
    )
    if not pipeline:
        raise HTTPException(status_code=400, detail="Could not build a valid scan pipeline for the target.")

    new_scan = Scan(
        scan_id=scan_id,
        target=scan_in.target,
        scan_mode=scan_in.scan_mode,
        scan_depth=scan_in.scan_depth,
        status="queued"
    )
    session.add(new_scan)
    await session.commit()
    await session.refresh(new_scan)

    task = {
        "db_id": new_scan.id,
        "scan_id": scan_id,
        "target": scan_in.target,
        "pipeline": pipeline,
    }

    queue = get_queue()
    await queue.enqueue_task(task)

    logger.info(f"Scan {scan_id} for target '{scan_in.target}' has been queued.", extra={"scan_id": scan_id})
    return new_scan


@router.get("/", response_model=List[ScanRead])
async def get_all_scans(session: AsyncSession = Depends(get_session), skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all scans.
    """
    result = await session.execute(select(Scan).offset(skip).limit(limit).order_by(Scan.created_at.desc()))
    scans = result.scalars().all()
    return scans


@router.get("/{scan_id}", response_model=ScanReadWithResults)
async def get_scan_details(scan_id: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve the details and results of a specific scan.
    """
    result = await session.execute(
        select(Scan)
        .where(Scan.scan_id == scan_id)
        .options(selectinload(Scan.results))
    )
    scan = result.scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan

@router.websocket("/ws/{scan_id}")
async def websocket_scan_output(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint to stream live output for a given scan ID.
    """
    await websocket.accept()
    subscriber = await get_live_output_subscriber()
    channel = f"scan_live_feed:{scan_id}" # Changed channel name
    
    try:
        async for message in subscriber.subscribe(channel):
            await websocket.send_text(message)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for scan ID: {scan_id}", extra={"scan_id": scan_id}) # Added extra
    except Exception as e:
        logger.error(f"WebSocket error for scan ID {scan_id}: {e}", extra={"scan_id": scan_id}) # Added extra
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

