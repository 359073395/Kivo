import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_ten_store_daily_batch import validate,STANDARD
s=json.loads(STANDARD.read_text(encoding='utf-8-sig'))
def base(count=10,date='2026-10-08'):
    items=[]
    for i in range(count):
        items.append(dict(sku=f'TEST-{i}',category_group=f'C{i}',similarity_group=f'U{i}',warehouse_row=i+3,real_product_evidence='synthetic-test-only',rights_evidence='synthetic-test-only',rights_review='passed',stock_sale_review='passed',keyword_source='synthetic-test-only',keyword_date='2026-10-08',main_image='synthetic-test-only',title_id='synthetic-test-only',details_attributes='synthetic-test-only',initial_versions=1))
    return dict(date=date,mandatory=True,items=items,bd_meaning='品牌认证',store_batches={st:[x['sku'] for x in items] for st in s['stores']})
tests=[]
b=base();assert validate(b)['allowed_for_execution_preparation'];tests.append('complete_ten_same_batch_all_stores')
b=base();b['items'][1]['similarity_group']='U0';assert not validate(b)['allowed_for_execution_preparation'];tests.append('reject_similar_products')
b=base();b['store_batches'][s['stores'][0]][0]='OTHER';assert not validate(b)['allowed_for_execution_preparation'];tests.append('reject_different_store_batch')
b=base();b['items'][0]['source_risk_inherited']=True;assert not validate(b)['allowed_for_execution_preparation'];tests.append('reject_merged_risk_note')
b=base();b['items'][0]['rights_review']='unknown';assert not validate(b)['allowed_for_execution_preparation'];tests.append('unknown_rights_not_safe')
b=base();b['items'][0]['initial_versions']=3;assert not validate(b)['allowed_for_execution_preparation'];tests.append('do_not_restore_three_versions')
b=base();b['bd_meaning']='达人建联';assert not validate(b)['allowed_for_execution_preparation'];tests.append('bd_brand_identity')
b=base();b['date']='2026-10-05';assert not validate(b)['allowed_for_execution_preparation'];tests.append('holiday_no_mandatory_batch')
vault=ROOT.parents[1]
assert (vault/'knowledge-base.json').exists()
for rel in ['SKILL.md','references/product-campaign-planning.md','modules/selection-engine/RUNBOOK.md','modules/listing-optimization/RUNBOOK.md']:
    assert '2026-09-30' in (ROOT/rel).read_text(encoding='utf-8-sig')
assert '每日每店5链接' in (vault/s['project']).read_text(encoding='utf-8-sig')
tests.append('restore_current_project_from_active_skill')
b=base(5,'2026-10-16');assert validate(b)['allowed_for_execution_preparation'];tests.append('new_plan_five_shared_skus_fifty_links')
b=base(10,'2026-10-16');assert not validate(b)['allowed_for_execution_preparation'];tests.append('new_plan_does_not_enforce_old_ten')
b=base(10,'2026-10-17');b['plan_rule_as_of']='2026-10-08';assert validate(b)['allowed_for_execution_preparation'];tests.append('already_published_ten_plan_history_retained')
b=base(5,'2026-10-16');b['items'][0]['initial_versions']=3;assert not validate(b)['allowed_for_execution_preparation'];tests.append('five_does_not_restore_three_versions')
feedback=s['morning_capacity_feedback'];assert feedback['elapsed_minutes'] is None and not feedback['replies_translation_samples_all_measured'] and not feedback['full_day_fifty_listings_capacity_verified'];tests.append('morning_feedback_does_not_invent_minutes_or_full_day_actuals')
b=base(5,'2026-10-19')
for x in b['items']:
    x.update(sourced_price='synthetic-source-only',recent_operating_evidence='synthetic-record-only',stock_sale_review='unknown',keyword_source=None,keyword_date=None,sku_created_at=None,company_site_coverage='unknown')
r=validate(b);assert r['allowed_for_execution_preparation'] and len(r['pre_upload_checks'])==5 and not r['platform_actions_authorized'];tests.append('current_week_unknown_stock_creation_market_deferred_not_fake_verified')
b['items'][0]['sourced_price']=None;assert not validate(b)['allowed_for_execution_preparation'];tests.append('current_week_real_price_still_required')
b['items'][0]['sourced_price']='synthetic-source-only';b['items'][0]['user_excluded']=True;assert not validate(b)['allowed_for_execution_preparation'];tests.append('current_week_user_excluded_still_blocks')
b['items'][0]['user_excluded']=False;b['date']='2026-10-25';assert not validate(b)['allowed_for_execution_preparation'];tests.append('temporary_override_not_permanent')
print(json.dumps({'passed':True,'scenarios':tests,'synthetic_business_results':False},ensure_ascii=False,indent=2))
