from config.celery import app

from apps.companies.models import Company
from .services import generate_company_insights


@app.task(queue="ai")
def generate_company_insights_task(company_id):
    company = Company.objects.get(id=company_id)
    insights = generate_company_insights(company)
    return [insight.id for insight in insights]
