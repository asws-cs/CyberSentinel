import asyncio
from sqlmodel import select
from datetime import datetime

from core.queue_manager import get_queue
from tools.tool_controller import ToolController
from core.risk_engine import get_risk_assessment
from database.db_connect import AsyncSessionLocal
from database.models import Scan, ScanResult, Report
from reports.json_exporter import generate_json_report
from reports.pdf_generator import generate_pdf_report
from utils.logger import logger
from utils.helpers import to_json

async def process_task(task: dict):
    """
    Processes a single scan task from the queue.
    """
    scan_id = task.get("scan_id")
    target = task.get("target")
    pipeline = task.get("pipeline")
    db_id = task.get("db_id")

    if not all([scan_id, target, pipeline, db_id]):
        logger.error(f"Invalid task received: {task}")
        return

    logger.info(f"[{scan_id}] Starting processing for target: {target}, db_id: {db_id}")

    async with AsyncSessionLocal() as session:
        # 1. Update scan status to 'in_progress'
        scan_record = await session.get(Scan, db_id)
        if not scan_record:
            logger.error(f"[{scan_id}] Scan record not found in database for db_id: {db_id}.")
            return
        logger.info(f"[{scan_id}] Scan record found. Current status: {scan_record.status}")
        scan_record.status = "in_progress"
        session.add(scan_record)
        await session.commit()
        await session.refresh(scan_record) # Refresh to ensure we have the latest state if needed

        results = []
        try:
            # 2. Run the tool pipeline
            controller = ToolController(scan_id)
            results = await controller.run_pipeline(pipeline)
            logger.info(f"[{scan_id}] Tool pipeline completed. Results count: {len(results)}")
        except Exception as e:
            logger.error(f"[{scan_id}] Failed to run tool pipeline: {type(e).__name__}: {e}", exc_info=True)
            scan_record.status = "failed"
            scan_record.finished_at = datetime.utcnow()
            scan_record.error_message = f"Tool pipeline failed: {str(e)}"
            session.add(scan_record)
            await session.commit()
            return # Exit early if pipeline fails

        total_score, severity, breakdown = 0, "unknown", {}
        try:
            # 3. Perform risk assessment
            total_score, severity, breakdown = get_risk_assessment(results)
            risk_assessment = {
                "total_risk_score": total_score,
                "severity": severity,
                "breakdown": breakdown,
            }
            logger.info(f"[{scan_id}] Risk assessment complete. Score: {total_score} ({severity})")
        except Exception as e:
            logger.error(f"[{scan_id}] Failed to perform risk assessment: {type(e).__name__}: {e}", exc_info=True)
            scan_record.status = "failed"
            scan_record.finished_at = datetime.utcnow()
            scan_record.error_message = f"Risk assessment failed: {str(e)}"
            session.add(scan_record)
            await session.commit()
            return # Exit early if risk assessment fails

        try:
            # 4. Save results to the database
            for result in results:
                findings_data = result.get("findings", result.get("error", {}))
                new_result = ScanResult(
                    scan_id=scan_id,
                    tool_name=result.get("tool_name", "unknown"),
                    findings_json=to_json(findings_data)
                )
                session.add(new_result)
            logger.info(f"[{scan_id}] Scan results saved to database.")
        except Exception as e:
            logger.error(f"[{scan_id}] Failed to save scan results: {type(e).__name__}: {e}", exc_info=True)
            scan_record.status = "failed"
            scan_record.finished_at = datetime.utcnow()
            scan_record.error_message = f"Saving results failed: {str(e)}"
            session.add(scan_record)
            await session.commit()
            return # Exit early if saving results fails

        # 5. Update scan status to 'completed'
        scan_record.status = "completed"
        scan_record.finished_at = datetime.utcnow()
        session.add(scan_record)

        try:
            # 6. Generate and save reports
            json_content_str = generate_json_report(scan_id, target, results, risk_assessment)
            pdf_content_bytes = await generate_pdf_report(scan_id, target, results, risk_assessment)

            json_report = Report(scan_id=scan_id, report_type='json', risk_score=total_score, severity=severity, content_blob=json_content_str.encode('utf-8'))
            pdf_report = Report(scan_id=scan_id, report_type='pdf', risk_score=total_score, severity=severity, content_blob=pdf_content_bytes)
            session.add(json_report)
            session.add(pdf_report)
            logger.info(f"[{scan_id}] Reports generated and saved.")
        except Exception as e:
            logger.error(f"[{scan_id}] Failed to generate or save reports: {type(e).__name__}: {e}", exc_info=True)
            # Do not return here, as results might still be useful even without reports
            scan_record.error_message = f"Report generation failed: {str(e)}"
        
        await session.commit()
        logger.info(f"[{scan_id}] Scan processing finished and results saved.")


async def worker_loop():
    """
    The main loop for the worker process.
    """
    queue = get_queue()
    logger.info("Worker loop started. Waiting for tasks...")
    while True:
        task_data = await queue.dequeue_task()
        if task_data:
            try:
                # The task is already a dict because of `decode_responses=True` in the queue's Redis client
                await process_task(task_data)
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing a task: {e}", exc_info=True)
        else:
            # If queue is empty, wait a bit before checking again
            await asyncio.sleep(5)


async def run_worker_async():
    # Initialize the queue before starting the loop
    from core.queue_manager import initialize_queue
    await initialize_queue()
    
    try:
        await worker_loop()
    except KeyboardInterrupt:
        logger.info("Worker process stopped by user.")

def run_worker():
    asyncio.run(run_worker_async())
