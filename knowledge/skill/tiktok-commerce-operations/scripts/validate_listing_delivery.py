"""Check a source-backed listing review, not product efficacy or marketing success."""
import argparse
import json
import re
from pathlib import Path


def resolve_vault():
    for parent in Path(__file__).resolve().parents:
        if (parent / 'knowledge-base.json').is_file():
            return parent
    raise ValueError('Active knowledge root not found above this script')


def normalize(value):
    return ' '.join(str(value).casefold().split())


def review(data):
    errors = []
    sku = str(data.get('sku', '')).strip()
    title = data.get('title', '')
    description = data.get('description', '')
    combined = normalize(title + '\n' + description)
    if not sku:
        errors.append('sku_missing')
    if not data.get('fact_sources'):
        errors.append('own_product_sources_missing')
    if not title or not description:
        errors.append('copy_missing')

    # These phrases must be grounded in the product, not selected for convenience.
    intents = data.get('intent_phrases', [])
    if not data.get('purchase_intent') or not intents or not data.get('intent_source'):
        errors.append('grounded_purchase_intent_missing')
    else:
        if not any(normalize(p) in normalize(title) for p in intents if p.strip()):
            errors.append('core_intent_lost_in_title')
        # Allow a product-name heading before the opening explanation.
        lead = '\n\n'.join(description.split('\n\n')[:2])
        if not any(normalize(p) in normalize(lead) for p in intents if p.strip()):
            errors.append('core_intent_lost_in_description_lead')

    terms = data.get('source_terms', [])
    if not terms:
        errors.append('keyword_comparison_missing')
    for item in terms:
        term = item.get('term', '')
        decision = item.get('decision')
        if not term or not item.get('source') or not item.get('reason'):
            errors.append('keyword_decision_incomplete:' + term)
        if decision not in ('keep', 'replace', 'exclude'):
            errors.append('keyword_decision_invalid:' + term)
        if decision in ('keep', 'replace'):
            output = item.get('output_term', term if decision == 'keep' else '')
            if not output or normalize(output) not in combined:
                errors.append('retained_keyword_absent:' + term)
            if not item.get('own_support'):
                errors.append('keyword_without_product_overlap:' + term)
        if decision == 'exclude' and normalize(term) in combined:
            errors.append('excluded_keyword_in_copy:' + term)

    for claim in data.get('claims', []):
        text = claim.get('text', '')
        if not text:
            errors.append('claim_text_missing')
            continue
        if normalize(text) in combined:
            if claim.get('status') != 'supported' or not claim.get('evidence_ref'):
                errors.append('unsupported_claim_in_copy:' + text)
            if claim.get('origin') in ('competitor_only', 'official_generated_only'):
                errors.append('external_copy_is_not_product_proof:' + text)

    audience = data.get('audience', {})
    status = audience.get('status')
    if status not in ('supported', 'unknown', 'not_applicable'):
        errors.append('audience_status_missing')
    if audience.get('requested') and not audience.get('handled'):
        errors.append('requested_audience_silently_omitted')
    if status == 'supported' and not audience.get('source'):
        errors.append('audience_evidence_missing')
    if status == 'unknown' and audience.get('phrase') and normalize(audience['phrase']) in combined:
        errors.append('unconfirmed_audience_in_copy')

    for rule in data.get('item_exceptions', []):
        if rule.get('applied') and rule.get('scope_sku') not in (sku, '*user_confirmed_global*'):
            errors.append('other_sku_exception_applied:' + str(rule.get('field')))

    judgment = data.get('quality_review', {})
    if judgment.get('generic_padding') is not False:
        errors.append('generic_padding_not_cleared')
    if judgment.get('natural_indonesian') is not True:
        errors.append('language_review_missing')
    if not judgment.get('concrete_changes'):
        errors.append('no_explained_improvement_over_input')
    if data.get('claims_search_or_sales_superiority') and not data.get('comparable_data_ref'):
        errors.append('performance_claim_without_comparable_data')
    if data.get('reported_title_length') is not None and data['reported_title_length'] != len(title):
        errors.append('wrong_title_character_count')

    response = data.get('response_markdown', '')
    blocks = re.findall(r'```[^\n]*\n(.*?)\n```', response, flags=re.S)
    if len(blocks) != 2 or blocks != [title, description]:
        errors.append('one_title_and_description_in_separate_blocks_required')
    for key in ('chinese_title_meaning', 'chinese_detail_summary'):
        value = data.get(key, '')
        if not value or not re.search(r'[\u4e00-\u9fff]', value) or value not in response:
            errors.append('chinese_explanation_missing:' + key)
    root = resolve_vault()
    return {
        'passed': not errors,
        'errors': errors,
        'title_characters': len(title),
        'vault_root': str(root),
        'contract': str(root / 'skill/tiktok-commerce-operations/references/listing-keyword-delivery.md'),
        'remote_execution_authorized': False,
        'scope': 'structured review consistency only; source truth, linguistic quality and efficacy require review',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review_json', type=Path)
    args = parser.parse_args()
    result = review(json.loads(args.review_json.read_text(encoding='utf-8-sig')))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
