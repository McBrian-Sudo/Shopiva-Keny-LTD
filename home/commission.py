from decimal import Decimal


# Shopiva platform commission schedule.
# The seller never chooses the rate; it is derived from the item's selling price.
# Rates increase as the product price increases.
COMMISSION_TIERS = (
    (Decimal("1000.00"), Decimal("5.00")),   # KSh 0 - 999.99
    (Decimal("5000.00"), Decimal("7.50")),   # KSh 1,000 - 4,999.99
    (Decimal("10000.00"), Decimal("10.00")), # KSh 5,000 - 9,999.99
    (Decimal("50000.00"), Decimal("12.50")), # KSh 10,000 - 49,999.99
)


def get_platform_commission_percent(price):
    """Return the platform commission percentage for a product selling price."""
    value = Decimal(str(price or "0.00"))
    if value < 0:
        value = Decimal("0.00")

    for threshold, rate in COMMISSION_TIERS:
        if value < threshold:
            return rate
    return Decimal("15.00")


def split_sale_amount(gross_amount):
    """Return (commission_rate, commission_amount, seller_amount) for a sale."""
    gross = Decimal(str(gross_amount or "0.00"))
    rate = get_platform_commission_percent(gross)
    commission = (gross * rate / Decimal("100")).quantize(Decimal("0.01"))
    seller_amount = gross - commission
    return rate, commission, seller_amount
