"""Behavior regressions for additive tools; all fixtures are synthetic."""
import copy
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import commerce_quality as q


def brief():
    text = 'Wax Rambut untuk Merapikan Rambut 15 g'
    item = dict(schema_version=1, brief_id='synthetic', version='v1',
                identity=dict(sku='SYNTHETIC-ONLY', market='ID', platform='tiktok_shop'),
                number_locale='id-ID', listing_targets=[],
                sources=[dict(id='pack', kind='product_image', ref='fixture:package', as_of='2026-10-19')],
                facts=[dict(id='weight', field='net_weight', value='15', unit='g', status='confirmed', source_ids=['pack']),
                       dict(id='use', field='use', value='Merapikan Rambut', unit='', status='user_confirmed', source_ids=['pack'])],
                core_selling_point=dict(text='Merapikan Rambut', fact_ids=['use']),
                forbidden_words=dict(reviewed=True, items=[]),
                deliverables=dict(title=text, description='Membantu merapikan rambut.'),
                required_keywords=[dict(text='Merapikan Rambut', surface='title', fact_ids=['use'])],
                numeric_bindings=[], claim_checks=[])
    bind(item)
    return item


def bind(item, field='net_weight'):
    item['numeric_bindings'] = []
    for surface, text in item['deliverables'].items():
        for mention in q.scan_numbers(text, item['number_locale']):
            item['numeric_bindings'].append(dict(surface=surface, start=mention['start'], end=mention['end'],
                                                fact_id='weight', field=field, context_reviewed=True))


def batch(rating=5, category=''):
    return dict(identity=dict(store='fixture-store', product_id='fixture-pid', sku='SYNTHETIC-ONLY'),
                origin='own_product', reviews=[dict(review_id='r1', rating=rating, text='fixture review',
                                                   category=category, source_ref='fixture:review', fact_ids=['use'])])


def iteration():
    return dict(identity=dict(store='fixture-store', product_id='fixture-pid', sku='SYNTHETIC-ONLY'),
                hypothesis='A clearer usage explanation may reduce misunderstanding.',
                changes=[dict(surface='description', before_ref='fixture:v1', after_ref='fixture:v2', reason='clarify use')],
                observations=None)


def observed():
    r = iteration()
    a = dict(identity=copy.deepcopy(r['identity']), start='2026-10-01', end='2026-10-03', source_ref='fixture:export-a',
             scope='same-channel-and-attribution', ready_for_comparison=True, readiness_basis='fixture complete window',
             metrics=dict(ctr=dict(kind='rate', definition='clicks/impressions', numerator=10, denominator=100)))
    b = copy.deepcopy(a)
    b.update(start='2026-10-04', end='2026-10-06', source_ref='fixture:export-b')
    b['metrics']['ctr']['numerator'] = 15
    r['observations'] = dict(before=a, after=b)
    return r


class CommerceQualityTests(unittest.TestCase):
    def test_same_supported_copy_passes_without_market_or_price_research(self):
        d = brief()
        r = q.check_brief(d)
        self.assertTrue(r['passed'], r)
        self.assertFalse(r['remote_execution_authorized'])
        self.assertIn('existing_listing_delivery_review_still_required', r['warnings'])

    def test_15_grams_cannot_support_15_years_even_if_bound(self):
        d = brief(); d['deliverables']['description'] = 'Untuk usia 15 tahun'; bind(d)
        self.assertFalse(q.check_brief(d)['passed'])

    def test_15_grams_cannot_support_15_kilograms(self):
        d = brief(); d['deliverables']['title'] = 'Merapikan Rambut 15 kg'; bind(d)
        self.assertFalse(q.check_brief(d)['passed'])

    def test_gram_kilogram_equivalence_with_indonesian_decimal(self):
        d = brief(); d['deliverables']['title'] = 'Merapikan Rambut 0,015 kg'; bind(d)
        self.assertTrue(q.check_brief(d)['passed'])

    def test_same_number_wrong_field_rejected(self):
        d = brief(); bind(d, field='age')
        self.assertFalse(q.check_brief(d)['passed'])

    def test_edited_text_cannot_reuse_old_binding(self):
        d = brief(); d['deliverables']['title'] = 'New ' + d['deliverables']['title']
        self.assertFalse(q.check_brief(d)['passed'])

    def test_added_video_number_must_be_bound(self):
        d = brief(); d['deliverables']['video_script'] = 'Hasil dalam 3 menit'
        self.assertFalse(q.check_brief(d)['passed'])

    def test_competitor_source_cannot_support_own_fact(self):
        d = brief(); d['sources'][0]['kind'] = 'competitor'
        self.assertFalse(q.check_brief(d)['passed'])

    def test_unused_unknown_fact_does_not_block_known_copy(self):
        d = brief(); d['facts'].append(dict(id='age', field='age', status='unknown', value=None))
        self.assertTrue(q.check_brief(d)['passed'])

    def test_claim_cannot_reference_unknown_fact(self):
        d = brief(); d['facts'].append(dict(id='age', field='age', status='unknown'))
        d['claim_checks'] = [dict(surface='description', quote=d['deliverables']['description'], fact_ids=['age'], context_reviewed=True)]
        self.assertFalse(q.check_brief(d)['passed'])

    def test_reviewed_empty_forbidden_list_passes_unreviewed_does_not(self):
        d = brief(); self.assertTrue(q.check_brief(d)['passed'])
        d['forbidden_words']['reviewed'] = False
        self.assertFalse(q.check_brief(d)['passed'])

    def test_no_implicit_platform_title_limit(self):
        d = brief(); d['deliverables']['title'] += ' bahan' * 50
        self.assertTrue(q.check_brief(d)['passed'])
        d['title_constraint'] = dict(max_characters=100, source_ref='fixture:current-field', checked_at='2026-10-19')
        self.assertFalse(q.check_brief(d)['passed'])

    def test_draft_without_pid_allowed_published_requires_pid(self):
        d = brief(); d['listing_targets'] = [dict(store='fixture-store', product_id=None, state='draft')]
        self.assertTrue(q.check_brief(d)['passed'])
        d['listing_targets'][0]['state'] = 'published'
        self.assertFalse(q.check_brief(d)['passed'])

    def test_known_hold_still_blocks(self):
        d = brief(); d['known_risks'] = [dict(id='fixture-risk', status='hold')]
        self.assertFalse(q.check_brief(d)['passed'])

    def test_all_positive_reviews_do_not_divide_by_zero(self):
        r = q.review_batch(batch(), brief())
        self.assertTrue(r['passed']); self.assertEqual(r['bad'], 0); self.assertEqual(r['bad_rate'], 0)
        self.assertEqual(r['patch_candidates'], [])
        json.dumps(r, allow_nan=False)

    def test_no_reviews_and_missing_ratings_are_unknown(self):
        d = batch(); d['reviews'] = []
        self.assertIsNone(q.review_batch(d)['bad_rate'])
        r = q.review_batch(batch(rating=''))
        self.assertIsNone(r['bad_rate']); self.assertEqual(r['unrated'], 1)

    def test_invalid_fractional_rating_not_counted_as_bad(self):
        r = q.review_batch(batch(rating=3.5))
        self.assertEqual(r['unrated'], 1); self.assertEqual(r['bad'], 0)

    def test_unknown_classification_is_not_fabricated(self):
        r = q.review_batch(batch(1, ''))
        self.assertEqual(r['unclassified_bad'], 1); self.assertFalse(r['attribution_complete'])

    def test_missing_accessory_goes_to_fulfillment(self):
        r = q.review_batch(batch(1, 'missing_accessories'), brief())
        patch = r['patch_candidates'][0]
        self.assertEqual(patch['route'], 'fulfillment_investigation'); self.assertFalse(patch['rewrite_allowed'])

    def test_grounded_misunderstanding_can_prepare_not_publish(self):
        patch = q.review_batch(batch(1, 'misunderstanding'), brief())['patch_candidates'][0]
        self.assertTrue(patch['rewrite_allowed']); self.assertFalse(patch['automatic_publish'])

    def test_competitor_review_cannot_authorize_own_copy(self):
        d = batch(1, 'misunderstanding'); d['origin'] = 'competitor'
        self.assertFalse(q.review_batch(d, brief())['patch_candidates'][0]['rewrite_allowed'])

    def test_duplicate_and_other_product_reviews_rejected(self):
        d = batch(); d['reviews'].append(copy.deepcopy(d['reviews'][0]))
        self.assertFalse(q.review_batch(d)['passed'])
        d = batch(); d['reviews'][0]['sku'] = 'other'
        self.assertFalse(q.review_batch(d)['passed'])

    def test_planned_iteration_not_mistaken_for_effect(self):
        r = q.check_iteration(iteration())
        self.assertTrue(r['passed']); self.assertEqual(r['state'], 'planned_not_measured')
        self.assertFalse(r['causal_claim_supported'])

    def test_same_scope_observations_only_describe_change(self):
        r = q.check_iteration(observed())
        self.assertEqual(r['state'], 'descriptive_comparison_ready')
        self.assertAlmostEqual(r['comparisons'][0]['delta'], .05)
        self.assertFalse(r['causal_claim_supported']); self.assertFalse(r['automatic_scale_or_delete'])

    def test_zero_denominator_is_unknown_not_zero_rate(self):
        d = observed(); d['observations']['after']['metrics']['ctr']['denominator'] = 0
        r = q.check_iteration(d)
        self.assertIsNone(r['comparisons'][0]['delta']); self.assertEqual(r['state'], 'needs_review')

    def test_cross_store_channel_definition_and_overlapping_period_rejected(self):
        for mutate in (
            lambda b: b['identity'].update(store='other'),
            lambda b: b.update(scope='other-channel'),
            lambda b: b['metrics']['ctr'].update(definition='orders/impressions'),
            lambda b: b.update(start='2026-10-03')):
            d = observed(); mutate(d['observations']['after'])
            self.assertFalse(q.check_iteration(d)['passed'])

    def test_missing_order_count_stays_unknown(self):
        d = observed()
        for w in d['observations'].values():
            w['metrics']['orders'] = dict(kind='count', definition='paid orders', value=None)
        r = q.check_iteration(d)
        self.assertIsNone(next(x for x in r['comparisons'] if x['metric'] == 'orders')['delta'])

    def test_multiple_changes_and_immature_windows_do_not_imply_success(self):
        d = observed(); d['changes'].append(dict(surface='title', before_ref='v1', after_ref='v2', reason='fixture'))
        d['observations']['after']['ready_for_comparison'] = False
        self.assertEqual(q.check_iteration(d)['state'], 'needs_review')

    def test_legacy_listing_validator_still_checks_actual_same_copy(self):
        from test_listing_delivery import prepared
        legacy = prepared(); d = brief()
        d['identity']['sku'] = legacy['sku']
        d['deliverables'] = {k: legacy[k] for k in ('title', 'description')}
        d['facts'][0].update(field='volume', value='300', unit='ml')
        d['required_keywords'] = []; bind(d, field='volume')
        self.assertTrue(q.check_brief(d, legacy)['passed'])
        legacy['title'] += ' changed'
        self.assertFalse(q.check_brief(d, legacy)['passed'])

    def test_cli_in_external_workdir_initializes_and_reviews_without_overwrite(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            try:
                os.chdir(tmp)
                self.assertEqual(q.main(['init', str(Path(tmp) / 'task')]), 0)
                self.assertEqual(q.main(['init', str(Path(tmp) / 'task')]), 1)
                path = Path(tmp) / 'good.json'; path.write_text(json.dumps(brief()), encoding='utf-8')
                result = Path(tmp) / 'result.json'
                self.assertEqual(q.main(['check', str(path), '--out', str(result)]), 0)
                self.assertTrue(json.loads(result.read_text(encoding='utf-8'))['passed'])
                self.assertEqual(q.main(['check', str(path), '--out', str(result)]), 1)
            finally:
                os.chdir(previous)

    def test_production_output_into_vault_rejected(self):
        with self.assertRaises(ValueError):
            q.external_output(q.SKILL / 'should-not-exist.json')


if __name__ == '__main__':
    unittest.main()
