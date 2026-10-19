"""Apply only explicitly confirmed warehouse Price 1 SKU aliases."""
import json
from pathlib import Path

def normalize(value):
    return ' '.join(str(value or '').strip().casefold().split())

def apply_confirmed_warehouse_aliases(records, alias_path=None):
    path=Path(alias_path) if alias_path else Path(__file__).resolve().parents[1]/'references'/'confirmed-warehouse-sku-aliases.json'
    out=dict(records)
    for alias in json.loads(path.read_text(encoding='utf-8'))['aliases']:
        if alias.get('confirmedBy')!='user':
            raise ValueError('Warehouse alias lacks direct user confirmation')
        key,target=normalize(alias['storeSku']),normalize(alias['warehouseSku'])
        if key not in out and target in out:
            out[key]=out[target]
    return out
