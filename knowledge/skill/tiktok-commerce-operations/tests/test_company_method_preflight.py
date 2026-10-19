import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPT))
from company_method_preflight import review, resolve_vault


def prepared(mode='paid_traffic_diagnosis'):
    return dict(mode=mode,project_state='new',prior_project_search='checked current projects',
                store='SYNTHETIC_STORE',sku='SYNTHETIC_SKU',evidence_refs=['fixture-only'],
                currency='IDR',timezone='Asia/Jakarta',period_start='2026-09-01',
                period_end='2026-09-07',attribution_definition='fixture same scope',
                account_state_checked=True,sale_state_checked=True,creative_rights_checked=True)


class CompanyMethods(unittest.TestCase):
    def test_external_cwd_resolves_actual_skill_and_reference(self):
        result=review(prepared(),tempfile.gettempdir())
        self.assertEqual(result['status'],'ready_for_local_preparation')
        self.assertTrue(Path(result['reference']).is_file())
        self.assertEqual(Path(result['vault_root']),Path('F:/Knowledge'))

    def test_existing_project_must_match_real_identity(self):
        with tempfile.TemporaryDirectory() as d:
            v=Path(d);(v/'knowledge-base.json').write_text('{}');(v/'项目').mkdir()
            (v/'项目/p.md').write_text('SYNTHETIC_STORE SYNTHETIC_SKU state=testing')
            c=prepared();c.update(project_state='existing',project_ref='项目/p.md',project_status_read=True)
            self.assertEqual(review(c,v)['status'],'ready_for_local_preparation')
            c['sku']='OTHER_SKU';self.assertIn('project_identity_mismatch:sku',review(c,v)['errors'])

    def test_source_roi_seven_not_executable_default(self):
        c=prepared();c['parameters']=[dict(name='roi',value=7,authority='company_manual',for_execution=True)]
        self.assertIn('parameter_not_approved:roi',review(c)['errors'])

    def test_listing_unknown_stock_and_price_isolation(self):
        c=prepared('listing');c.update(inventory=10000,action_domains=['price'])
        r=review(c);self.assertIn('inventory_unknown',r['errors']);self.assertIn('COM-004_listing_price_isolation',r['errors'])

    def test_sudden_drop_checks_account_before_creative_blame(self):
        c=prepared();c['account_state_checked']=False
        self.assertIn('prerequisite_unchecked:account_state_checked',review(c)['errors'])

    def test_immature_zero_order_never_retired(self):
        c=prepared();c.update(retire_for_zero_orders=True,window_mature=False,sample_sufficiency_reviewed=True)
        self.assertIn('COM-013_014_insufficient_retirement_evidence',review(c)['errors'])

    def test_overlapping_gmv_cannot_be_subtracted(self):
        c=prepared('weekly_review');c['subtract_overlapping_attribution']=True
        self.assertIn('attribution_not_additive',review(c)['errors'])

    def test_sample_is_not_publication_or_ad_authorization(self):
        c=prepared('creator_outreach');c.update(campaign_brief='fixture',sample_received=True,ad_use_planned=True)
        r=review(c);self.assertIn('sample_received_is_not_published',r['cautions']);self.assertIn('ad_rights_unverified',r['errors'])

    def test_fake_outreach_rejected(self):
        c=prepared('creator_outreach');c.update(campaign_brief='fixture',fabricated_claims=['pretend sample was sent'])
        self.assertIn('untruthful_or_evasive_action',review(c)['errors'])

    def test_current_notice_required_for_appeal(self):
        self.assertIn('appeal_notice_or_evidence_unverified',review(prepared('appeal_preparation'))['errors'])

    def test_content_recovers_baseline_and_routes_separately(self):
        c=prepared('content_preparation');r=review(c)
        self.assertEqual(r['route'],'tiktok-content-system');self.assertEqual(r['status'],'blocked')
        c.update(product_fact_card='fixture',source_rights='fixture',production_baseline='approved fixture')
        self.assertEqual(review(c)['status'],'ready_for_local_preparation')

    def test_import_request_routes_to_distillation(self):
        self.assertEqual(review({'intent':'knowledge_distillation'})['route'],'knowledge-distillation')

    def test_preflight_never_grants_external_permission(self):
        c=prepared();c.update(external_action='adjust_budget',current_task_approved=True)
        self.assertFalse(review(c)['remote_execution_authorized'])


if __name__=='__main__':unittest.main()
