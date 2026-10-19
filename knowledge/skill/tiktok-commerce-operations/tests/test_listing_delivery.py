import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_listing_delivery import review, resolve_vault


def render(data):
    data['response_markdown'] = ('标题\n```text\n' + data['title'] + '\n```\n' +
        data['chinese_title_meaning'] + '\n详情\n```text\n' + data['description'] +
        '\n```\n' + data['chinese_detail_summary'])
    return data


def prepared():
    # Synthetic tests represent the user's failure modes, not efficacy evidence.
    return render(dict(
        sku='Ginseng Shampoo', fact_sources=['fixture: own product description'],
        purchase_intent='Care for shedding-hair concerns without promising fast growth',
        intent_phrases=['perawatan rambut rontok'], intent_source='fixture: own intended use',
        title='Ginseng Shampoo untuk Perawatan Rambut Rontok Pria dan Wanita 300ml',
        description='Ginseng Shampoo untuk perawatan rambut rontok dan kebersihan kulit kepala.\n\nIsi 300ml.',
        source_terms=[
            dict(term='Ginseng Shampoo', source='own original', decision='keep', reason='product type', own_support='fixture: user confirmed ginseng'),
            dict(term='Penumbuh Rambut Cepat', source='official copy', decision='replace',
                 output_term='Perawatan Rambut Rontok', reason='retain supported concern without unproven speed', own_support='fixture: own intended use'),
        ],
        claims=[dict(text='Penumbuh Rambut Cepat', status='unverified', evidence_ref='', origin='official_generated_only')],
        audience=dict(status='supported', requested=True, handled=True, source='fixture: men and women'),
        item_exceptions=[], claims_search_or_sales_superiority=False,
        quality_review=dict(generic_padding=False, natural_indonesian=True,
                            concrete_changes=['retain core concern; remove only fast-growth promise']),
        chinese_title_meaning='人参洗发水，男女适用，掉发护理需求。',
        chinese_detail_summary='详情说明清洁用途与规格。',
    ))


class ListingDeliveryTests(unittest.TestCase):
    def test_supported_intent_retained_without_fast_growth(self):
        self.assertTrue(review(prepared())['passed'])

    def test_product_heading_before_intro_is_allowed(self):
        d=prepared();d['description']='GINSENG SHAMPOO\n\n'+d['description']
        self.assertTrue(review(render(d))['passed'])

    def test_generic_cleaning_cannot_replace_supported_core_intent(self):
        d=prepared(); d['title']='Ginseng Shampoo 300ml untuk Membersihkan Rambut'
        d['description']='Shampo untuk menjaga kebersihan rambut.'
        errors=review(render(d))['errors']
        self.assertIn('core_intent_lost_in_title',errors)
        self.assertIn('core_intent_lost_in_description_lead',errors)

    def test_silent_keyword_deletion_is_rejected(self):
        d=prepared();d['source_terms'][0]['reason']=''
        self.assertIn('keyword_decision_incomplete:Ginseng Shampoo',review(d)['errors'])

    def test_kept_keyword_must_appear(self):
        d=prepared();d['source_terms'].append(dict(term='Kulit Berminyak',source='own',decision='keep',reason='need',own_support='fixture'))
        self.assertIn('retained_keyword_absent:Kulit Berminyak',review(d)['errors'])

    def test_competitor_term_needs_own_overlap(self):
        d=prepared();d['source_terms'][0]['own_support']=''
        self.assertIn('keyword_without_product_overlap:Ginseng Shampoo',review(d)['errors'])

    def test_unconfirmed_claim_not_usable_even_with_footnote(self):
        d=prepared();d['title']+=' Penumbuh Rambut Cepat';render(d)
        d['response_markdown']+='\n待确认，暂缺实测。'
        self.assertIn('unsupported_claim_in_copy:Penumbuh Rambut Cepat',review(d)['errors'])

    def test_official_copy_is_not_effect_proof(self):
        d=prepared();d['title']+=' Penumbuh Rambut Cepat';render(d)
        d['claims'][0].update(status='supported',evidence_ref='official generated paragraph')
        self.assertIn('external_copy_is_not_product_proof:Penumbuh Rambut Cepat',review(d)['errors'])

    def test_age_request_cannot_be_silently_ignored(self):
        d=prepared();d['audience'].update(status='unknown',handled=False)
        self.assertIn('requested_audience_silently_omitted',review(d)['errors'])

    def test_unknown_age_not_added_to_recommended_title(self):
        d=prepared();d['audience'].update(status='unknown',phrase='untuk anak')
        d['title']+=' untuk anak'
        self.assertIn('unconfirmed_audience_in_copy',review(render(d))['errors'])

    def test_not_applicable_age_does_not_force_children(self):
        d=prepared();d['audience']=dict(status='not_applicable',requested=False,handled=True)
        self.assertTrue(review(d)['passed'])

    def test_wax_brand_weight_exception_not_transferred(self):
        d=prepared();d['item_exceptions']=[dict(field='omit_weight',scope_sku='Pink Sleek Stick',applied=True)]
        self.assertIn('other_sku_exception_applied:omit_weight',review(d)['errors'])

    def test_semantic_comparison_not_sales_proof(self):
        d=prepared();d['claims_search_or_sales_superiority']=True
        self.assertIn('performance_claim_without_comparable_data',review(d)['errors'])

    def test_chinese_and_separate_copy_blocks_required(self):
        d=prepared();d['response_markdown']='```text\n'+d['title']+'\n'+d['description']+'\n```'
        errors=review(d)['errors']
        self.assertIn('one_title_and_description_in_separate_blocks_required',errors)
        self.assertIn('chinese_explanation_missing:chinese_title_meaning',errors)

    def test_generic_filler_fails_review(self):
        d=prepared();d['quality_review']['generic_padding']=True
        self.assertIn('generic_padding_not_cleared',review(d)['errors'])

    def test_empty_facts_do_not_pass(self):
        d=prepared();d['fact_sources']=[]
        self.assertIn('own_product_sources_missing',review(d)['errors'])

    def test_character_count_is_measured_not_assumed(self):
        d=prepared();d['reported_title_length']=255
        self.assertIn('wrong_title_character_count',review(d)['errors'])
        d['reported_title_length']=len(d['title'])
        self.assertTrue(review(d)['passed'])

    def test_external_working_directory_recovers_live_route(self):
        before=Path.cwd()
        with tempfile.TemporaryDirectory() as external:
            try:
                os.chdir(external);root=resolve_vault()
                skill=root/'skill/tiktok-commerce-operations'
                self.assertIn('references/listing-keyword-delivery.md',(skill/'SKILL.md').read_text(encoding='utf-8-sig'))
                self.assertIn('listing-keyword-delivery.md',(skill/'modules/listing-optimization/RUNBOOK.md').read_text(encoding='utf-8-sig'))
                self.assertTrue(Path(review(prepared())['contract']).is_file())
                self.assertFalse(review(prepared())['remote_execution_authorized'])
            finally:
                os.chdir(before)


if __name__=='__main__':
    unittest.main()
