from datetime import date

from sqlalchemy import extract, func, select

from app.extensions import db
from app.models import AIInsight, Expense, Receipt


class AIInsightService:
    def get_or_generate_monthly_insight(self, user_id: int, month: date | None = None) -> AIInsight | None:
        target_month = (month or date.today()).replace(day=1)
        existing = db.session.scalar(
            select(AIInsight).where(AIInsight.user_id == user_id).where(AIInsight.month == target_month)
        )
        if existing is not None:
            return existing

        rows = db.session.execute(
            select(Expense.category, func.coalesce(func.sum(Expense.total_amount), 0))
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .where(extract("year", Expense.purchased_at) == target_month.year)
            .where(extract("month", Expense.purchased_at) == target_month.month)
            .group_by(Expense.category)
            .order_by(func.sum(Expense.total_amount).desc())
        ).all()
        if not rows:
            return None

        largest_category = rows[0][0].value
        total = sum(float(row[1]) for row in rows)
        summary = f"You spent {total:,.2f} across {len(rows)} categories this month."
        habits = f"Your largest spending area was {largest_category}, which is the first place to review for recurring costs."
        suggestions = "Set a category target for next month, review duplicate purchases, and move predictable bills into a planned budget."

        insight = AIInsight(
            user_id=user_id,
            month=target_month,
            summary=summary,
            largest_category=largest_category,
            spending_habits=habits,
            saving_suggestions=suggestions,
            model_name="rules-v1",
        )
        db.session.add(insight)
        db.session.commit()
        return insight
