from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import extract, func, select

from app.extensions import db
from app.models import Expense, Receipt


@dataclass(frozen=True)
class DashboardMetrics:
    total_spending: Decimal
    monthly_spending: Decimal
    highest_expense: Expense | None
    receipt_count: int
    recent_receipts: list[Receipt]
    category_labels: list[str]
    category_values: list[float]
    monthly_labels: list[str]
    monthly_values: list[float]


class DashboardService:
    def get_metrics(self, user_id: int) -> DashboardMetrics:
        today = date.today()
        month_start = date(today.year, today.month, 1)

        total_spending = db.session.scalar(
            select(func.coalesce(func.sum(Expense.total_amount), 0))
            .join(Receipt)
            .where(Receipt.user_id == user_id)
        )
        monthly_spending = db.session.scalar(
            select(func.coalesce(func.sum(Expense.total_amount), 0))
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .where(Expense.purchased_at >= month_start)
        )
        highest_expense = db.session.scalar(
            select(Expense)
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .order_by(Expense.total_amount.desc())
        )
        receipt_count = db.session.scalar(
            select(func.count(Receipt.id)).where(Receipt.user_id == user_id)
        )
        recent_receipts = db.session.scalars(
            select(Receipt)
            .where(Receipt.user_id == user_id)
            .order_by(Receipt.created_at.desc())
            .limit(6)
        ).all()
        category_labels, category_values = self._category_breakdown(user_id)
        monthly_labels, monthly_values = self._monthly_trend(user_id)

        return DashboardMetrics(
            total_spending=Decimal(total_spending or 0),
            monthly_spending=Decimal(monthly_spending or 0),
            highest_expense=highest_expense,
            receipt_count=int(receipt_count or 0),
            recent_receipts=recent_receipts,
            category_labels=category_labels,
            category_values=category_values,
            monthly_labels=monthly_labels,
            monthly_values=monthly_values,
        )

    def _category_breakdown(self, user_id: int) -> tuple[list[str], list[float]]:
        rows = db.session.execute(
            select(Expense.category, func.coalesce(func.sum(Expense.total_amount), 0))
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .group_by(Expense.category)
            .order_by(func.sum(Expense.total_amount).desc())
        ).all()
        return [row[0].value for row in rows], [float(row[1]) for row in rows]

    def _monthly_trend(self, user_id: int) -> tuple[list[str], list[float]]:
        months = _last_six_months()
        rows = db.session.execute(
            select(
                extract("year", Expense.purchased_at),
                extract("month", Expense.purchased_at),
                func.coalesce(func.sum(Expense.total_amount), 0),
            )
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .where(Expense.purchased_at.is_not(None))
            .group_by(extract("year", Expense.purchased_at), extract("month", Expense.purchased_at))
        ).all()
        totals = {(int(row[0]), int(row[1])): float(row[2]) for row in rows}
        labels = [month.strftime("%b %Y") for month in months]
        values = [totals.get((month.year, month.month), 0.0) for month in months]
        return labels, values


def _last_six_months() -> list[date]:
    current = date.today().replace(day=1)
    months = []
    for offset in range(5, -1, -1):
        month = current
        for _ in range(offset):
            month = (month - timedelta(days=1)).replace(day=1)
        months.append(month)
    return months
