from enum import Enum
from typing import List

from tortoise import fields
from tortoise.models import Model


class SalesProcessingStatus(Enum):
    REGISTERED = "registered"
    PARSING_STARTED = "parsing_started"
    PARSED = "parsed"
    LLM_RESPONSE_GENERATED = "llm_response_generated"

    FAILED = "failed"


class Sale(Model):
    id = fields.IntField(pk=True)
    product_id = fields.IntField()
    product_name = fields.CharField(max_length=255)
    quantity = fields.IntField()
    price = fields.FloatField()
    category = fields.CharField(max_length=255)

    created_at = fields.DatetimeField(auto_now_add=True)

    sales_report = fields.ForeignKeyField(
        'models.SalesReport',
        related_name='sales',
        on_delete=fields.CASCADE
    )

    class Meta:
        table = 'sales'


class SalesReport(Model):
    id = fields.IntField(pk=True)
    sales_date = fields.DateField(null=True)
    preprocessed_sales = fields.TextField(null=True)
    analysis = fields.TextField(null=True)  # Response from LLM

    status = fields.CharEnumField(SalesProcessingStatus, default=SalesProcessingStatus.REGISTERED)
    last_log = fields.TextField(null=True)  # Fills in case of exception

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'sales_reports'


async def save_sales_to_db(sales: List[dict]):
    await Sale.bulk_create([Sale(**s) for s in sales])
