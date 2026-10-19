"""Synthetic COM-014 gate regressions; never SKU facts or volume defaults."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'scripts/campaign_plan_gate.py'
spec = importlib.util.spec_from_file_location('campaign_plan_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    # All evidence below is synthetic and explicitly unsuitable for live use.
    p = {key: 'synthetic_' + key for key in (
        'plan_id', 'sku', 'store', 'purchase_reason', 'product_evidence',
        'window', 'volume_rationale', 'review_criteria', 'resource_limits')}
    p.update(path='build', restoration={'status':'new', 'search_evidence':'synthetic no existing match'})
    p['base_sets'] = [dict(title='draft', cover='draft', detail='draft',
        hypothesis=f'angle_{i}', audience='fixture', scene='fixture', evidence='fixture',
        destination='draft link map', cover_selling_points=2) for i in range(3)]
    p['channels'] = {name: dict(owner='fixture', schedule='synthetic window',
        dependencies='fixture link readiness', volume='synthetic batch target', feedback='fixture')
        for name in ('listing', 'owned_video', 'creator_video', 'ads')}
    p['evidence_review'] = {name: {'status':'passed', 'evidence':'synthetic reviewed evidence'}
        for name in ('product_claims', 'real_images', 'link_identity', 'policy')}
    return p


class CampaignGateTests(unittest.TestCase):
    def test_resolves_skill_vault_from_outside(self):
        with tempfile.TemporaryDirectory() as outside:
            root = gate.resolve_vault(outside)
        self.assertEqual(root, MODULE.parents[3])
        self.assertTrue((root / 'knowledge-base.json').is_file())

    def test_build_ready_without_online_authorization(self):
        result = gate.review(fixture())
        self.assertEqual(result['decision'], 'ready_for_preparation')
        self.assertFalse(result['online_action_authorized'])
        self.assertFalse(result['business_effectiveness_verified'])

    def test_follow_requires_dated_migration_evidence(self):
        p = fixture(); p['path'] = 'follow'
        self.assertIn('follow_evidence_incomplete', gate.review(p)['errors'])
        p['benchmark'] = dict(source='fixture', date='synthetic date',
                              signal='synthetic signal', transfer_difference='fixture difference')
        self.assertFalse(gate.review(p)['errors'])

    def test_restores_exact_project_and_rejects_wrong_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / '项目').mkdir()
            project = root / '项目' / 'fixture.md'
            p = fixture()
            project.write_text('\n'.join(p[k] for k in ('plan_id', 'sku', 'store')), encoding='utf-8')
            p['restoration'] = dict(status='existing', project_ref='项目/fixture.md', current_status='fixture in progress')
            with patch.object(gate, 'resolve_vault', return_value=root):
                self.assertFalse(gate.review(p)['errors'])
                p['sku'] = 'another_sku'
                self.assertIn('existing_project_identity_mismatch', gate.review(p)['errors'])

    def test_missing_images_blocks_preparation(self):
        p = fixture(); p['evidence_review']['real_images']['status'] = 'unknown'
        self.assertEqual(gate.review(p)['decision'], 'blocked_for_preparation')

    def test_three_cosmetic_copies_are_insufficient(self):
        p = fixture(); p['base_sets'] = [copy.deepcopy(p['base_sets'][0]) for _ in range(3)]
        self.assertIn('distinct_hypotheses_missing', gate.review(p)['errors'])

    def test_three_point_preference_is_not_platform_rejection(self):
        p = fixture(); p['base_sets'][0]['cover_selling_points'] = 4
        r = gate.review(p)
        self.assertFalse(r['errors']); self.assertTrue(r['notes'])

    def test_missing_cycle_and_volume_cannot_pass(self):
        p = fixture(); p.pop('window'); p.pop('volume_rationale')
        self.assertIn('missing:window', gate.review(p)['errors'])
        self.assertIn('missing:volume_rationale', gate.review(p)['errors'])

    def test_channel_can_be_inapplicable_with_reason(self):
        p = fixture(); p['channels']['ads'] = dict(status='not_applicable', reason='no authorized paid test')
        self.assertFalse(gate.review(p)['errors'])
        p['channels']['ads'].pop('reason')
        self.assertIn('channel_omission_unexplained:ads', gate.review(p)['errors'])

    def test_zero_orders_alone_never_switches(self):
        p = fixture(); p['requested_decision'] = 'switch_product'
        p['observation'] = {'orders':0}
        self.assertEqual(gate.review(p)['decision'], 'review_or_continue_test_not_switch')

    def test_sufficient_test_considers_switch_not_deletion(self):
        p = fixture(); p['requested_decision'] = 'switch_product'
        p['observation'] = {k: True for k in ('coverage_sufficient', 'window_mature',
             'sale_available', 'data_verified', 'no_meaningful_signal')}
        p['observation'].update(sufficiency_evidence='fixture coverage', outcome_evidence='fixture results')
        self.assertEqual(gate.review(p)['decision'], 'consider_switch_not_delete')
        for field in ('coverage_sufficient', 'window_mature', 'sale_available', 'data_verified', 'no_meaningful_signal'):
            q = copy.deepcopy(p); q['observation'][field] = None
            self.assertEqual(gate.review(q)['decision'], 'review_or_continue_test_not_switch')


if __name__ == '__main__':
    unittest.main()
