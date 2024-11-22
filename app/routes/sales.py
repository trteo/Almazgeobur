from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from tortoise.transactions import in_transaction

from app.database import SalesReport, SalesProcessingStatus
from app.tasks import process_sales_data, process_sales_data_task

router = APIRouter()


@router.post("/upload_file", summary="Upload sales data in XML format")
async def upload_sales_file(file: UploadFile = File(...)):
    try:
        async with in_transaction() as connection:
            if not file.filename.endswith(".xml"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not XML")

            xml_data = await file.read()

            # Create empty response row that will be field with prepared data and LLM response in celery task
            report = await SalesReport.create(
                status=SalesProcessingStatus.REGISTERED
            )
            # await process_sales_data(xml_content=xml_data, report_id=report.id)
            process_sales_data_task.apply_async(kwargs={'xml_content': xml_data, 'report_id': report.id}, countdown=2)

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={"message": "File accepted and processing started", "report_id": report.id},
            )
    except Exception as e:
        raise e
        # raise HTTPException(status_code=500, detail=str(e))
