"""Local COM-014 planning preflight; no remote actions or market-effect claims.

Human/agent review fields describe evidence already read; the gate cannot attest
to their truth. Runtime plans belong outside the portable knowledge vault.
"""
from pathlib import Path
import argparse
import json
import os


def resolve_vault(start=None):
    """Follow the actual Skill location before the configured fallback."""
    origins = [Path(start or Path.cwd()).resolve(), Path(__file__).resolve()]
    for origin in origins:
        for candidate in (origin, *origin.parents):
            if (candidate / 'knowledge-base.json').is_file():
                return candidate
    configured = os.environ.get('KNOWLEDGE_BASE_ROOT')
    if configured and (Path(configured) / 'knowledge-base.json').is_file():
        return Path(configured).resolve()
    fallback = Path('D:/Knowledge')
    if (fallback / 'knowledge-base.json').is_file():
        return fallback
    raise FileNotFoundError('knowledge-base.json not found')


def review(plan, start=None):
    root = resolve_vault(start)
    errors, notes = [], []
    required = ('plan_id', 'sku', 'store', 'purchase_reason', 'product_evidence',
                'window', 'volume_rationale', 'review_criteria', 'resource_limits')
    errors.extend('missing:' + key for key in required if not plan.get(key))
    if plan.get('path') not in ('build', 'follow'):
        errors.append('choose_build_or_follow')
    if plan.get('path') == 'follow':
        ref = plan.get('benchmark') or {}
        if not all(ref.get(k) for k in ('source', 'date', 'signal', 'transfer_difference')):
            errors.append('follow_evidence_incomplete')

    state = plan.get('restoration') or {}
    project = state.get('project_ref')
    if state.get('status') == 'existing':
        if not project:
            errors.append('existing_project_missing')
        else:
            target = (root / project).resolve()
            allowed = (root / '项目').resolve()
            if not target.is_relative_to(allowed) or not target.is_file():
                errors.append('existing_project_missing')
            else:
                text = target.read_text(encoding='utf-8-sig')
                identity = (plan.get('plan_id'), plan.get('sku'), plan.get('store'))
                if not all(v and v in text for v in identity):
                    errors.append('existing_project_identity_mismatch')
                if not state.get('current_status'):
                    errors.append('existing_project_status_unread')
    elif state.get('status') == 'new':
        if not state.get('search_evidence'):
            errors.append('project_search_not_recorded')
    else:
        errors.append('project_not_restored')

    sets = plan.get('base_sets') or []
    if len(sets) < 3:
        errors.append('three_base_sets_missing')
    hypotheses = []
    for i, item in enumerate(sets):
        if not all(item.get(k) for k in ('title', 'cover', 'detail', 'hypothesis',
                                        'audience', 'scene', 'evidence', 'destination')):
            errors.append(f'base_set_incomplete:{i}')
        hypotheses.append(item.get('hypothesis'))
        count = item.get('cover_selling_points')
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            errors.append(f'cover_points_unknown:{i}')
        elif count > 3:
            notes.append(f'prefer_at_most_three_cover_points:{i}')
    if len(set(hypotheses)) < 3:
        errors.append('distinct_hypotheses_missing')

    channels = plan.get('channels') or {}
    for name in ('listing', 'owned_video', 'creator_video', 'ads'):
        channel = channels.get(name) or {}
        if channel.get('status') == 'not_applicable':
            if not channel.get('reason'):
                errors.append('channel_omission_unexplained:' + name)
        elif not all(channel.get(k) for k in ('owner', 'schedule', 'dependencies',
                                              'volume', 'feedback')):
            errors.append('channel_plan_incomplete:' + name)

    gates = plan.get('evidence_review') or {}
    for name in ('product_claims', 'real_images', 'link_identity', 'policy'):
        if (gates.get(name) or {}).get('status') != 'passed' or not (gates.get(name) or {}).get('evidence'):
            errors.append('evidence_review_needed:' + name)

    decision = 'blocked_for_preparation' if errors else 'ready_for_preparation'
    if plan.get('requested_decision') == 'switch_product' and not errors:
        obs = plan.get('observation') or {}
        required_review = ('coverage_sufficient', 'window_mature', 'sale_available',
                           'data_verified', 'no_meaningful_signal')
        checks = [obs.get(k) is True for k in required_review]
        if all(checks) and obs.get('sufficiency_evidence') and obs.get('outcome_evidence'):
            decision = 'consider_switch_not_delete'
        else:
            decision = 'review_or_continue_test_not_switch'
    return {'vault': str(root), 'mode': 'campaign_planning', 'decision': decision,
            'errors': errors, 'notes': notes, 'online_action_authorized': False,
            'business_effectiveness_verified': False,
            'limitation': 'Checks supplied state and evidence references, not market truth or semantic quality.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    args = parser.parse_args()
    result = review(json.loads(Path(args.plan).read_text(encoding='utf-8-sig')))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result['errors'] else 0)
