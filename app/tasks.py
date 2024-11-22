from celery import Celery
from loguru import logger
from tortoise import Tortoise

from app.database import save_sales_to_db, SalesProcessingStatus, SalesReport
from app.src.xml_parser import parse_sales_data
from asgiref.sync import async_to_sync

from settings.config import TORTOISE_ORM

celery = Celery("tasks", broker="redis://localhost:6379/0")  # TODO redo for docker


async def tortoise_init():
    await Tortoise.init(config=TORTOISE_ORM)


@celery.task
def process_sales_data_task(xml_content: bytes, report_id: int):
    logger.info(f'xml_content: {xml_content}, report_id: {report_id}')
    async_to_sync(process_sales_data)(xml_content=xml_content, report_id=report_id)


async def process_sales_data(xml_content: bytes, report_id: int):
    await tortoise_init()
    logger.info(await SalesReport.all())
    report = await SalesReport.get(id=report_id)

    try:
        # Parse XML
        sales_data = await parse_sales_data(xml_content.decode("utf-8"), report=report)
        await save_sales_to_db(sales_data)

        # Update report status
        report.status = SalesProcessingStatus.PARSED
        await report.save()
    except Exception as e:
        # Log exception to db
        if report:
            report.status = SalesProcessingStatus.FAILED
            report.last_log = str(e)
            await report.save()
        raise e
