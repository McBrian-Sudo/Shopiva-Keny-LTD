from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ROOT / "home" / "views.py"
text = VIEWS.read_text(encoding="utf-8")

seller_functions = (
    "seller_dashboard",
    "seller_product_edit",
    "seller_product_toggle",
    "seller_product_add",
    "seller_product_delete",
    "seller_request_payout",
)

for name in seller_functions:
    pattern = re.compile(
        rf'(@login_required\(login_url="customer_login"\)\n(def {name}\([^\n]*\):)',
        re.M,
    )
    text, count = pattern.subn(
        rf'@login_required(login_url="seller_login")\n\2',
        text,
        count=1,
    )

VIEWS.write_text(text, encoding="utf-8")
print("Seller protected views now use the dedicated seller login page.")
