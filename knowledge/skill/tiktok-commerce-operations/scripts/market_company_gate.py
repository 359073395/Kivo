"""Deterministic evidence checks; not a product recommender or listing approval."""
import json
from validate_ten_store_daily_batch import STANDARD,traffic_test_override

def assess(company_rows, market_rows, *, head_checked=False, entry_case=False, materials_ready=False, plan_date=None, recent_operating_evidence=False, explicit_new_arrival=False, known_product_risk=False):
    company_values=[r.get('units') for r in company_rows]
    company_known=bool(company_values) and all(isinstance(x,(int,float)) for x in company_values)
    known=[x for x in company_values if isinstance(x,(int,float))]
    same_external=[r for r in market_rows if r.get('same_exact_sku') is True and isinstance(r.get('units'),(int,float))]
    if any(x>=1000 for x in known) or any(r['units']>=1000 for r in same_external):
        return {'state':'exclude_1000','company_max':max(known,default=None),'company_positive_credit':0}
    external=[r for r in market_rows if r.get('owner')=='external_verified' and r.get('comparable') is True and r.get('current') is True and r.get('url') and isinstance(r.get('units'),(int,float)) and r['units']>0]
    reasons=[]
    if not external:reasons.append('independent_market_evidence_missing')
    if not company_known:reasons.append('company_competition_unknown')
    if not head_checked:reasons.append('unfiltered_head_not_checked')
    if not entry_case:reasons.append('entry_space_not_evidenced')
    if not materials_ready:reasons.append('product_materials_not_ready')
    standard=json.loads(STANDARD.read_text(encoding='utf-8-sig'))
    if traffic_test_override(standard,plan_date):
        blocking=[]
        if known_product_risk:blocking.append('known_product_risk')
        if not materials_ready:blocking.append('product_materials_not_ready')
        if not (recent_operating_evidence or explicit_new_arrival):blocking.append('trial_lead_evidence_missing')
        return {'state':'needs_product_evidence' if blocking else 'eligible_for_traffic_test_preparation','reasons':blocking,'non_blocking_market_gaps':[r for r in reasons if r!='product_materials_not_ready'],'company_max':max(known,default=None),'company_positive_credit':0,'external_evidence_count':len(external),'market_validation_complete':False,'platform_actions_authorized':False,'stock_check':'before_manual_upload','temporary_override_end':'2026-10-24'}
    return {'state':'needs_evidence' if reasons else 'eligible_for_manual_review','reasons':reasons,'company_max':max(known,default=None),'company_positive_credit':0,'external_evidence_count':len(external),'preferred_market_count':sum(50<=r['units']<=500 for r in external)}
