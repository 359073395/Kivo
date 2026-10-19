"""Validate the user's ten-store initial-test batch; never publishes or certifies IP rights."""
import json,sys
from pathlib import Path
STANDARD=Path(__file__).resolve().parents[1]/'references'/'ten-store-daily-test-standard.json'
def traffic_test_override(standard, date):
    """Date-bound user exception for preparation; never a publishing approval."""
    rule=standard.get('temporary_traffic_test_override',{})
    return bool(date and rule.get('status')=='active_project' and rule.get('start_date','')<=date<=rule.get('end_date',''))

def targets_for_plan(standard, rule_as_of=None):
    """Use plan-generation date for history; absent date means current parameters."""
    keys=('daily_unique_skus','daily_per_store_skus','daily_total_listing_target')
    revision=standard.get('quantity_revision',{})
    if rule_as_of and rule_as_of < revision.get('effective_for_plans_generated_from',''):
        return {k:revision['historical_daily_targets'][k] for k in keys}
    return {k:standard[k] for k in keys}

def validate(batch,standard=None):
    s=standard or json.loads(STANDARD.read_text(encoding='utf-8-sig'))
    issues=[]
    date=batch.get('date','')
    trial=traffic_test_override(s,date)
    pre_upload_checks=[]
    targets_for_date=targets_for_plan(s,batch.get('plan_rule_as_of',date))
    count=targets_for_date['daily_unique_skus']
    if s['holiday']['start']<=date<=s['holiday']['end'] and batch.get('mandatory',False):issues.append('holiday_cannot_be_mandatory')
    rows=batch.get('items',[])
    keys=[x.get('sku','') for x in rows]
    if len(rows)!=count or len(set(keys))!=count or any(not k or k=='待选' for k in keys):issues.append('need_'+str(count)+'_exact_distinct_skus')
    categories=[x.get('category_group') for x in rows]
    similar=[x.get('similarity_group') for x in rows]
    if len(set(categories))!=count or any(not x for x in categories):issues.append('categories_not_diverse_or_unchecked')
    if len(set(similar))!=count or any(not x for x in similar):issues.append('similar_products_or_unchecked')
    required=['warehouse_row','real_product_evidence','rights_evidence','keyword_source','keyword_date','main_image','title_id','details_attributes']
    if trial:
        required=[f for f in required if f not in ('keyword_source','keyword_date')]+['sourced_price']
    for i,x in enumerate(rows):
        if x.get('source_risk_flag') or x.get('source_risk_inherited'):issues.append(f'item_{i+1}_source_ip_or_imitation_flag')
        if x.get('rights_review')!='passed':issues.append(f'item_{i+1}_rights_or_sale_unverified')
        stock=x.get('stock_sale_review')
        if trial and stock in (None,'unknown','pending_pre_upload'):
            pre_upload_checks.append({'sku':x.get('sku'),'check':'stock_sale_review','verified':False})
        elif stock!='passed':issues.append(f'item_{i+1}_rights_or_sale_unverified')
        if trial and not (x.get('recent_operating_evidence') or x.get('explicit_new_arrival_evidence')):
            issues.append(f'item_{i+1}_trial_lead_evidence_missing')
        if trial and (x.get('known_product_risk') or x.get('user_excluded') or x.get('clearance') or x.get('in_transit')):
            issues.append(f'item_{i+1}_known_risk_or_user_exclusion')
        if any(not x.get(f) for f in required):issues.append(f'item_{i+1}_missing_evidence')
        if x.get('initial_versions')!=1:issues.append(f'item_{i+1}_old_multi_version_initial_test')
    targets=batch.get('store_batches',{})
    if set(targets)!=set(s['stores']):issues.append('store_set_mismatch')
    for store,values in targets.items():
        if len(values)!=targets_for_date['daily_per_store_skus'] or set(values)!=set(keys):issues.append('store_batch_not_same:'+store)
    if batch.get('bd_meaning')!=s['bd_meaning']:issues.append('bd_is_brand_certification_not_creator_outreach')
    return {'allowed_for_execution_preparation':not issues,'issues':issues,'platform_actions_authorized':False,'standard':s['scope'],'quantity_targets':targets_for_date,'temporary_traffic_test_override':trial,'pre_upload_checks':pre_upload_checks,'market_validation_certified':False}
if __name__=='__main__':
    b=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    out=validate(b);print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['allowed_for_execution_preparation'] else 2)
