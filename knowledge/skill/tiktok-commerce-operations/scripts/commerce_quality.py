"""Local supplements to existing listing review; never publish or infer product truth.

Uses only Python's standard library. Production JSON/CSV and reports belong outside
the knowledge vault. Templates are initialized without overwriting existing files.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys

SKILL = Path(__file__).resolve().parents[1]
SURFACES = ('title', 'description', 'image_text', 'video_script')
OWN_SOURCES = {'product_document', 'product_image', 'measurement', 'user_confirmation'}
CONFIRMED = {'confirmed', 'user_confirmed'}
NUMBER = re.compile(r'\d+(?:[.,]\d+)*')
UNITS = {
    'g': ('mass', Decimal(1)), 'kg': ('mass', Decimal(1000)), 'mg': ('mass', Decimal('.001')),
    'ml': ('volume', Decimal(1)), 'l': ('volume', Decimal(1000)),
    'mm': ('length', Decimal(1)), 'cm': ('length', Decimal(10)), 'm': ('length', Decimal(1000)),
    'w': ('power', Decimal(1)), 'v': ('voltage', Decimal(1)), 'mah': ('capacity', Decimal(1)),
    'pcs': ('count', Decimal(1)), 'buah': ('count', Decimal(1)),
    'tahun': ('years', Decimal(1)), 'year': ('years', Decimal(1)), 'years': ('years', Decimal(1)),
    'jam': ('time', Decimal(3600)), 'menit': ('time', Decimal(60)),
    'detik': ('time', Decimal(1)), '%': ('percent', Decimal(1)), '': ('unitless', Decimal(1)),
}
UNIT_RE = re.compile(r'\s*(mah|tahun|years?|menit|detik|buah|pcs|jam|kg|mg|ml|mm|cm|g|l|m|w|v|%)(?!\w)', re.I)
CATEGORIES = {
    'misunderstanding': 'listing_clarity', 'usage_difficulty': 'instructions_review',
    'missing_accessories': 'fulfillment_investigation', 'quality': 'quality_investigation',
    'logistics': 'logistics_investigation', 'expectation_gap': 'fact_and_expectation_review',
    'other': 'manual_review',
}


def normalized(text):
    return ' '.join(str(text).casefold().split())


def number(value, locale='canonical'):
    if isinstance(value, bool) or value is None:
        raise ValueError('missing_or_invalid_number')
    text = str(value).strip()
    if locale == 'id-ID':
        if not re.fullmatch(r'\d+(?:,\d+)?|\d{1,3}(?:\.\d{3})+(?:,\d+)?', text):
            raise ValueError('ambiguous_indonesian_number')
        text = text.replace('.', '').replace(',', '.')
    try:
        result = Decimal(text)
    except InvalidOperation:
        raise ValueError('invalid_number') from None
    if not result.is_finite():
        raise ValueError('non_finite_number')
    return result


def iso_date(value):
    return date.fromisoformat(value)


def output(errors, **kwargs):
    return dict(passed=not errors, errors=errors, remote_execution_authorized=False, **kwargs)


def fact_index(brief):
    errors, usable = [], {}
    sources = {}
    for item in brief.get('sources', []):
        sid = item.get('id')
        if not sid or sid in sources:
            errors.append('source_id_missing_or_duplicate')
        else:
            sources[sid] = item
    seen = set()
    for fact in brief.get('facts', []):
        fid = fact.get('id')
        if not fid or fid in seen:
            errors.append('fact_id_missing_or_duplicate')
            continue
        seen.add(fid)
        if fact.get('status') not in CONFIRMED:
            continue  # Unknown/conflicting fields may remain, but cannot ground claims.
        refs = fact.get('source_ids', [])
        own = [sources.get(ref, {}) for ref in refs]
        valid = bool(refs) and all(
            s.get('kind') in OWN_SOURCES and s.get('ref') and s.get('as_of') for s in own)
        try:
            for source in own:
                iso_date(source.get('as_of', ''))
        except (ValueError, TypeError):
            valid = False
        if not valid or not fact.get('field') or fact.get('value') in (None, ''):
            errors.append('confirmed_fact_without_own_evidence:' + str(fid))
        else:
            usable[fid] = fact
    return usable, errors


def scan_numbers(text, locale):
    found = []
    for match in NUMBER.finditer(text):
        tail = UNIT_RE.match(text, match.end())
        unit = tail.group(1).lower() if tail else ''
        end = tail.end() if tail else match.end()
        try:
            value = str(number(match.group(), locale))
            issue = None
        except ValueError as exc:
            value, issue = None, str(exc)
        found.append(dict(start=match.start(), end=end, text=text[match.start():end],
                          value=value, unit=unit, issue=issue))
    return found


def check_brief(brief, listing_review=None):
    errors, warnings = [], []
    identity = brief.get('identity', {})
    if brief.get('schema_version') != 1:
        errors.append('schema_version_must_be_1')
    for key in ('brief_id', 'version'):
        if not brief.get(key):
            errors.append(key + '_missing')
    if not identity.get('sku'):
        errors.append('exact_sku_missing')
    if identity.get('market') != 'ID' or identity.get('platform') != 'tiktok_shop':
        errors.append('this_profile_requires_indonesia_tiktok')
    if brief.get('number_locale') not in ('id-ID', 'canonical'):
        errors.append('number_locale_required')
    facts, fact_errors = fact_index(brief)
    errors.extend(fact_errors)
    if not facts:
        errors.append('no_supported_product_facts')
    selling = brief.get('core_selling_point', {})
    if not selling.get('text') or not selling.get('fact_ids') or any(
            fid not in facts for fid in selling.get('fact_ids', [])):
        errors.append('core_selling_point_requires_own_fact_refs')
    forbidden = brief.get('forbidden_words', {})
    if forbidden.get('reviewed') is not True or not isinstance(forbidden.get('items'), list):
        errors.append('forbidden_words_review_incomplete')
    # An explicitly reviewed empty list is valid; do not force invented bans.
    for risk in brief.get('known_risks', []):
        if risk.get('status') == 'hold':
            errors.append('known_risk_hold:' + str(risk.get('id', 'unspecified')))
    targets = set()
    for target in brief.get('listing_targets', []):
        key = (target.get('store'), target.get('product_id'))
        if not key[0] or key in targets:
            errors.append('listing_target_missing_store_or_duplicate')
        targets.add(key)
        if target.get('state') not in ('draft', 'published'):
            errors.append('listing_target_state_invalid')
        if target.get('state') == 'published' and not key[1]:
            errors.append('published_target_requires_product_id')
    texts = brief.get('deliverables', {})
    if not any(texts.get(s) for s in SURFACES):
        errors.append('no_deliverable_text')
    mentions, used_bindings = [], set()
    bindings = brief.get('numeric_bindings', [])
    for surface, text in texts.items():
        if surface not in SURFACES or not isinstance(text, str):
            errors.append('invalid_text_surface:' + surface)
            continue
        for word in forbidden.get('items', []):
            if word.strip() and normalized(word) in normalized(text):
                errors.append('forbidden_term_in_' + surface + ':' + word)
        for mention in scan_numbers(text, brief.get('number_locale', 'id-ID')):
            mention['surface'] = surface
            matches = [(i, b) for i, b in enumerate(bindings) if b.get('surface') == surface
                       and b.get('start') == mention['start'] and b.get('end') == mention['end']]
            location = f"{surface}:{mention['start']}"
            if mention['issue']:
                errors.append('number_parse_requires_review:' + location)
            if len(matches) != 1:
                errors.append('numeric_binding_missing_or_duplicate:' + location)
                mention['status'] = 'needs_binding'
            else:
                idx, binding = matches[0]
                used_bindings.add(idx)
                fact = facts.get(binding.get('fact_id'))
                if not fact or binding.get('field') != fact.get('field'):
                    errors.append('numeric_field_or_evidence_mismatch:' + location)
                elif binding.get('context_reviewed') is not True:
                    errors.append('numeric_context_review_required:' + location)
                else:
                    try:
                        left_unit = UNITS[mention['unit']]
                        right_unit = UNITS[str(fact.get('unit', '')).lower()]
                        left = number(mention['value']) * left_unit[1]
                        right = number(fact['value']) * right_unit[1]
                        if left_unit[0] != right_unit[0] or left != right:
                            errors.append('numeric_value_or_unit_mismatch:' + location)
                    except (ValueError, KeyError):
                        errors.append('numeric_format_requires_review:' + location)
                mention['status'] = 'bound_requires_semantic_review'
            mentions.append(mention)
    if len(used_bindings) != len(bindings):
        errors.append('stale_or_unused_numeric_bindings')
    title = texts.get('title', '')
    constraints = brief.get('title_constraint')
    if constraints:
        limit = constraints.get('max_characters')
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0 or not constraints.get('source_ref'):
            errors.append('title_limit_requires_positive_value_and_source')
        else:
            try:
                iso_date(constraints.get('checked_at', ''))
            except (ValueError, TypeError):
                errors.append('title_limit_verification_date_invalid')
            if len(title) > limit:
                errors.append('title_exceeds_supplied_limit')
    else:
        warnings.append('title_length_measured_platform_limit_not_asserted')
    for keyword in brief.get('required_keywords', []):
        if not keyword.get('fact_ids') or any(fid not in facts for fid in keyword['fact_ids']):
            errors.append('keyword_without_own_fact_refs:' + str(keyword.get('text', '')))
        surface = keyword.get('surface', 'title')
        if not keyword.get('text') or normalized(keyword['text']) not in normalized(texts.get(surface, '')):
            errors.append('required_keyword_missing:' + str(keyword.get('text', '')))
    for claim in brief.get('claim_checks', []):
        text = texts.get(claim.get('surface'), '')
        if not claim.get('quote') or claim['quote'] not in text:
            errors.append('claim_quote_missing_or_stale')
        if claim.get('context_reviewed') is not True or not claim.get('fact_ids') or any(
                fid not in facts for fid in claim.get('fact_ids', [])):
            errors.append('claim_requires_own_evidence_and_context_review')
    existing = None
    if listing_review is not None:
        from validate_listing_delivery import review
        if any(listing_review.get(k) != texts.get(k) for k in ('title', 'description')) or listing_review.get('sku') != identity.get('sku'):
            errors.append('existing_listing_review_payload_mismatch')
        existing = review(listing_review)
        errors.extend('listing_review:' + e for e in existing['errors'])
    elif title or texts.get('description'):
        warnings.append('existing_listing_delivery_review_still_required')
    return output(errors, warnings=warnings, title_characters=len(title), numeric_mentions=mentions,
                  existing_listing_review=existing, visual_review_required=True,
                  scope='local consistency precheck; not proof of efficacy, complete claim coverage, platform compliance or marketing effect')


def review_batch(batch, brief=None):
    errors, warnings = [], []
    identity = batch.get('identity', {})
    if not all(identity.get(k) for k in ('store', 'product_id', 'sku')):
        errors.append('review_batch_requires_store_product_id_sku')
    origin = batch.get('origin')
    if origin not in ('own_product', 'competitor'):
        errors.append('review_origin_required')
    facts = {}
    if brief is not None:
        facts, e = fact_index(brief)
        errors.extend(e)
        if brief.get('identity', {}).get('sku') != identity.get('sku'):
            errors.append('review_brief_sku_mismatch')
    rows = batch.get('reviews', [])
    if not rows:
        warnings.append('no_reviews_no_conclusions')
    seen, categories, patches = set(), Counter(), []
    good = neutral = bad = unrated = unclassified = 0
    for row in rows:
        rid = row.get('review_id')
        if not rid or rid in seen:
            errors.append('review_id_missing_or_duplicate:' + str(rid))
            continue
        seen.add(rid)
        if not row.get('source_ref') or not row.get('text'):
            errors.append('review_source_or_text_missing:' + rid)
        if any(row.get(k) and row[k] != identity.get(k) for k in ('store', 'product_id', 'sku')):
            errors.append('mixed_product_reviews:' + rid)
            continue
        try:
            rating = number(row.get('rating'))
            if rating != int(rating) or rating < 1 or rating > 5:
                raise ValueError('invalid_rating')
        except ValueError:
            unrated += 1
            continue
        if rating >= 4:
            good += 1
        elif rating == 3:
            neutral += 1
        else:
            bad += 1
            cat = row.get('category', '')
            if cat not in CATEGORIES:
                unclassified += 1
                continue
            categories[cat] += 1
            refs = row.get('fact_ids') or []
            supported = bool(refs) and all(fid in facts for fid in refs)
            route = CATEGORIES[cat]
            patches.append(dict(review_id=rid, category=cat, route=route,
                                state='ready_for_human_review' if supported and origin == 'own_product' else 'needs_product_evidence',
                                source_ref=row.get('source_ref'), fact_ids=refs,
                                rewrite_allowed=cat in ('misunderstanding', 'usage_difficulty') and supported and origin == 'own_product',
                                automatic_publish=False))
    rated = good + neutral + bad
    if unrated or unclassified:
        warnings.append('missing_rating_or_classification_remains_unknown')
    if origin == 'competitor':
        warnings.append('competitor_reviews_are_hypotheses_not_own_product_facts')
    return output(errors, warnings=warnings, total_rows=len(rows), rated=rated, unrated=unrated,
                  good=good, neutral=neutral, bad=bad, bad_rate=bad / rated if rated else None,
                  attribution=dict(categories), unclassified_bad=unclassified,
                  attribution_denominator=bad, attribution_complete=sum(categories.values()) == bad,
                  patch_candidates=patches, scope='counts of supplied classifications; causes and remedies require review')


def check_iteration(record):
    errors, warnings, comparison = [], [], []
    identity = record.get('identity', {})
    if not all(identity.get(k) for k in ('store', 'product_id', 'sku')):
        errors.append('iteration_requires_store_product_id_sku')
    if not record.get('hypothesis') or not record.get('changes'):
        errors.append('hypothesis_and_changes_required')
    for change in record.get('changes', []):
        if change.get('surface') not in SURFACES or not all(change.get(k) for k in ('before_ref', 'after_ref', 'reason')):
            errors.append('change_record_incomplete')
        if change.get('before_ref') == change.get('after_ref'):
            errors.append('distinct_version_refs_required')
    if len(record.get('changes', [])) > 1:
        warnings.append('multiple_changes_no_single_change_attribution')
    if not record.get('observations'):
        return output(errors, warnings=warnings, state='planned_not_measured', comparisons=[], causal_claim_supported=False)
    windows = record.get('observations', {})
    if set(windows) != {'before', 'after'}:
        return output(errors + ['both_observation_windows_required'], warnings=warnings,
                      state='needs_data', comparisons=[], causal_claim_supported=False)
    days = {}
    dates = {}
    for label, window in windows.items():
        if window.get('identity') != identity:
            errors.append('observation_identity_mismatch:' + label)
        if not window.get('source_ref') or not window.get('scope'):
            errors.append('observation_source_and_scope_required:' + label)
        if window.get('ready_for_comparison') is not True or not window.get('readiness_basis'):
            warnings.append('observation_not_ready:' + label)
        try:
            start, end = iso_date(window['start']), iso_date(window['end'])
            if end < start:
                raise ValueError('reversed')
            days[label], dates[label] = (end - start).days + 1, (start, end)
        except (ValueError, KeyError, TypeError):
            errors.append('invalid_observation_dates:' + label)
    if len(dates) == 2 and dates['before'][1] >= dates['after'][0]:
        errors.append('observation_windows_overlap_or_reversed')
    if windows['before'].get('scope') != windows['after'].get('scope'):
        errors.append('observation_scope_mismatch')
    old, new = windows['before'].get('metrics', {}), windows['after'].get('metrics', {})
    if not old or not new:
        warnings.append('metrics_missing')
    for key in sorted(set(old) | set(new)):
        a, b = old.get(key, {}), new.get(key, {})
        result = dict(metric=key, delta=None, status='unknown')
        if not a.get('definition') or a.get('definition') != b.get('definition') or a.get('kind') != b.get('kind'):
            errors.append('metric_definition_mismatch:' + key)
        else:
            try:
                values = []
                for metric in (a, b):
                    if metric.get('kind') == 'rate':
                        numerator, denominator = number(metric.get('numerator')), number(metric.get('denominator'))
                        if denominator <= 0 or numerator < 0 or numerator > denominator:
                            raise ValueError('unknown_rate')
                        values.append(numerator / denominator)
                    elif metric.get('kind') == 'count':
                        value = number(metric.get('value'))
                        if value < 0 or value != int(value) or days.get('before') != days.get('after'):
                            raise ValueError('count_window_or_value_invalid')
                        values.append(value)
                    else:
                        raise ValueError('unsupported_metric_kind')
                result.update(before=float(values[0]), after=float(values[1]),
                              delta=float(values[1] - values[0]), status='descriptive_only')
            except ValueError:
                warnings.append('metric_unknown_or_not_comparable:' + key)
        comparison.append(result)
    blocked = bool(errors or warnings or not comparison)
    return output(errors, warnings=warnings, state='needs_review' if blocked else 'descriptive_comparison_ready',
                  comparisons=comparison, causal_claim_supported=False, automatic_scale_or_delete=False)


def load(path):
    value = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('JSON_object_required')
    return value


def external_output(path):
    target = Path(path).resolve()
    vault = SKILL.parents[1]
    if target.is_relative_to(vault):
        raise ValueError('production_output_must_be_outside_knowledge_vault')
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('directory', type=Path)
    for command in ('check', 'reviews', 'iterate'):
        p = sub.add_parser(command)
        p.add_argument('input', type=Path)
        p.add_argument('--out', type=Path)
        if command == 'check':
            p.add_argument('--listing-review', type=Path)
        if command == 'reviews':
            p.add_argument('--brief', type=Path)
            p.add_argument('--csv', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            destination = external_output(args.directory / 'product-brief.json').parent
            templates = sorted((SKILL / 'assets/commerce-quality').glob('*'))
            if any((destination / p.name).exists() for p in templates):
                raise ValueError('refusing_to_replace_existing_template')
            for template in templates:
                (destination / template.name).write_bytes(template.read_bytes())
            result = output([], state='templates_created_not_validated', directory=str(destination))
        else:
            data = load(args.input)
            if args.command == 'check':
                result = check_brief(data, load(args.listing_review) if args.listing_review else None)
            elif args.command == 'reviews':
                if args.csv:
                    with args.csv.open(encoding='utf-8-sig', newline='') as stream:
                        data['reviews'] = list(csv.DictReader(stream))
                    for row in data['reviews']:
                        row['fact_ids'] = [s.strip() for s in row.get('fact_ids', '').split(';') if s.strip()]
                result = review_batch(data, load(args.brief) if args.brief else None)
            else:
                result = check_iteration(data)
            if args.out:
                destination = external_output(args.out)
                if destination.exists():
                    raise ValueError('refusing_to_replace_existing_report')
                destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        result = output(['input_or_output_error:' + str(exc)], state='needs_correction')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
