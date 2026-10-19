"""2026-10-10 user rule: Npcs SKU price equals exact base final unit price * N."""
from decimal import Decimal
import re

def validate_npcs_records(records):
    exact = {r['sku']: r for r in records}
    errors = []
    for sku, row in exact.items():
        match = re.fullmatch(r'([1-9]\d*)(?i:pcs)(.+)', sku)
        if not match or row.get('status') != '可用':
            continue
        quantity, base_sku = int(match[1]), match[2]
        base = exact.get(base_sku)
        unit = base.get('selected_price') if base else None
        if base is None or base.get('status') != '可用' or unit is None or not Decimal(str(unit)).is_finite() or Decimal(str(unit)) <= 0:
            errors.append({'sku': sku, 'base_sku': base_sku, 'reason': 'Npcs exact base final unit price missing or unusable; do not use an independent pack quote'})
            continue
        expected = Decimal(str(unit)) * quantity
        actual = row.get('selected_price')
        if actual is None or Decimal(str(actual)) != expected:
            errors.append({'sku': sku, 'base_sku': base_sku, 'quantity': quantity, 'expected': str(expected), 'actual': str(actual), 'reason': 'Npcs final price must equal exact base final unit price times quantity'})
    return errors
