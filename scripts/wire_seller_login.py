"""Legacy helper retained for reference.

Seller authentication is now enforced centrally by seller_auth.seller_login_required
and the seller routes in shopiva/urls.py. This script is intentionally a no-op so
old automation cannot rewrite the protected views.
"""

print("Seller login protection is managed centrally; no file rewrites required.")
