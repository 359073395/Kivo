import unittest,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from market_company_gate import assess
def m(units=100,owner='external_verified',same=False):
    return dict(units=units,owner=owner,same_exact_sku=same,comparable=True,current=True,url='https://example.test/product/evidence')
class Regression(unittest.TestCase):
    def test_kalodata_company_not_external(self):
        r=assess([{'units':433}],[m(404,'company')]);self.assertEqual(r['external_evidence_count'],0)
    def test_any_shop_1000_not_low_shop_only(self):
        self.assertEqual(assess([{'units':80},{'units':1000}],[m()])['state'],'exclude_1000')
    def test_same_exact_market_high_excluded(self):
        self.assertEqual(assess([{'units':12}],[m(1010,same=True),m(100)])['state'],'exclude_1000')
    def test_category_high_not_exact_exclusion(self):
        self.assertNotEqual(assess([{'units':12}],[m(3000,same=False)])['state'],'exclude_1000')
    def test_unknown_owner_not_external(self):
        self.assertEqual(assess([{'units':1}],[m(owner='unknown')])['external_evidence_count'],0)
    def test_low_company_without_market_not_opportunity(self):
        self.assertIn('independent_market_evidence_missing',assess([{'units':1}],[m(0)])['reasons'])
    def test_company_better_never_positive_credit(self):
        a=assess([{'units':10}],[m()]);b=assess([{'units':900}],[m()]);self.assertEqual(a['company_positive_credit'],b['company_positive_credit']);self.assertGreater(b['company_max'],a['company_max'])
    def test_unknown_company_not_zero(self):
        self.assertIn('company_competition_unknown',assess([],[m()])['reasons'])
    def test_filtered_search_without_head_blocked(self):
        self.assertIn('unfiltered_head_not_checked',assess([{'units':10}],[m()],entry_case=True,materials_ready=True)['reasons'])
    def test_positive_branch_requires_entry_and_material(self):
        self.assertEqual(assess([{'units':10}],[m()],head_checked=True,entry_case=True,materials_ready=True)['state'],'eligible_for_manual_review')
    def test_outside_vault_entry_recovers_new_rule(self):
        r=assess([],[],plan_date='2026-10-19',materials_ready=True,recent_operating_evidence=True)
        self.assertEqual(r['state'],'eligible_for_traffic_test_preparation')
        self.assertFalse(r['market_validation_complete']);self.assertFalse(r['platform_actions_authorized'])
        vault=ROOT.parents[1];config=json.loads((ROOT/'references/ten-store-daily-test-standard.json').read_text(encoding='utf-8-sig'))
        self.assertEqual(config['market_company_competition']['company_sales_role'],'competition_reference_not_positive_score')
        self.assertIn('market-opportunity-company-competition.md',(ROOT/'SKILL.md').read_text(encoding='utf8'))
        self.assertTrue((vault/config['market_company_competition']['source']).is_file())
    def test_current_week_known_product_risk_still_blocks(self):
        r=assess([],[],plan_date='2026-10-24',materials_ready=True,explicit_new_arrival=True,known_product_risk=True)
        self.assertIn('known_product_risk',r['reasons'])
    def test_week_override_expires_without_changing_general_method(self):
        r=assess([],[],plan_date='2026-10-25',materials_ready=True,recent_operating_evidence=True)
        self.assertEqual(r['state'],'needs_evidence')
if __name__=='__main__':unittest.main()
