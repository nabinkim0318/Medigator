from fastapi import APIRouter
import logging
from api.core.schemas import SummaryIn, SummaryOut
from api.services.llm.tasks.summarize import run as summarize_run

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])

@router.post("", response_model=SummaryOut)
async def summarize_endpoint(body: SummaryIn):
    logger.info("Summary request received")
    try:
        result = await summarize_run(body)
        logger.info("Summary generated successfully")
        return result
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise