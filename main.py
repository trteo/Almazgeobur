from fastapi import FastAPI
import uvicorn
from app.routes import sales, reports
from tortoise.contrib.fastapi import register_tortoise

from settings.config import TORTOISE_ORM

app = FastAPI(
    title="XML Parser & AI Analyzer",
    version="1.0.0",
    description="Сервис для анализа данных о продажах"
)

register_tortoise(app=app, config=TORTOISE_ORM, generate_schemas=False)

app.include_router(sales.router, prefix="/sales", tags=["Sales"])
# app.include_router(reports.router, prefix="/reports", tags=["Reports"])


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        port=8002,
        host='0.0.0.0',
        log_config='settings/logger_config.json',
    )
