from dataclasses import dataclass
from math import ceil

from sqlalchemy import asc, desc, func, or_, select

from app.extensions import db
from app.models import Expense, Receipt


@dataclass(frozen=True)
class Pagination:
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        return max(1, ceil(self.total / self.per_page))

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages


class ReceiptHistoryService:
    SORT_COLUMNS = {
        "date": Expense.purchased_at,
        "merchant": Expense.merchant_name,
        "amount": Expense.total_amount,
        "category": Expense.category,
        "created": Receipt.created_at,
    }

    def search(self, user_id: int, args):
        page = max(int(args.get("page", 1) or 1), 1)
        per_page = 10
        query_text = (args.get("q") or "").strip()
        category = (args.get("category") or "").strip()
        sort = args.get("sort") or "created"
        direction = args.get("direction") or "desc"

        filters = [Receipt.user_id == user_id]
        if query_text:
            pattern = f"%{query_text}%"
            filters.append(
                or_(
                    Receipt.original_filename.ilike(pattern),
                    Expense.merchant_name.ilike(pattern),
                    Expense.receipt_number.ilike(pattern),
                )
            )
        if category:
            filters.append(Expense.category == category)

        total = db.session.scalar(
            select(func.count(func.distinct(Receipt.id)))
            .select_from(Receipt)
            .join(Expense, isouter=True)
            .where(*filters)
        )
        sort_column = self.SORT_COLUMNS.get(sort, Receipt.created_at)
        sort_expression = desc(sort_column) if direction == "desc" else asc(sort_column)
        receipts = db.session.scalars(
            select(Receipt)
            .join(Expense, isouter=True)
            .where(*filters)
            .order_by(sort_expression)
            .offset((page - 1) * per_page)
            .limit(per_page)
        ).all()
        return receipts, Pagination(page=page, per_page=per_page, total=int(total or 0))
