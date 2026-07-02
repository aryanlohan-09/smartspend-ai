from enum import Enum


class ExpenseCategory(str, Enum):
    FOOD = "Food"
    GROCERY = "Grocery"
    SHOPPING = "Shopping"
    MEDICAL = "Medical"
    TRAVEL = "Travel"
    ENTERTAINMENT = "Entertainment"
    BILLS = "Bills"
    FUEL = "Fuel"
    OTHER = "Other"


class ReceiptStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    DUPLICATE = "duplicate"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"
    WALLET = "Wallet"
    BANK_TRANSFER = "Bank Transfer"
    OTHER = "Other"
    UNKNOWN = "Unknown"
