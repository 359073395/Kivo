"""Scoped COM-015 preparation checks; never performs or authorizes remote work.

Structured fields record evidence inspected by the operator. This validator does
not prove evidence truth, statistical sufficiency, or causal explanations.
"""
import argparse
import json
from pathlib import Path
from campaign_plan_gate import resolve_vault

ROUTES = {
    'campaign_planning': ('tiktok-commerce-operations', '01'),
    'selection': ('tiktok-commerce-operations', '01'),
    'listing': ('tiktok-commerce-operations', '02'),
    'paid_traffic_diagnosis': ('tiktok-commerce-operations', '03'),
    'content_preparation': ('tiktok-content-system', '04'),
    'creator_outreach': ('tiktok-creator-outreach', '05'),
    'weekly_review': ('tiktok-commerce-operations', '06'),
    'appeal_preparation': ('tiktok-commerce-operations', '06'),
}


def review(context, start=None):
    root = resolve_vault(start)
    if context.get('intent') == 'knowledge_distillation':
        return {'route': 'knowledge-distillation', 'status': 'route_upstream',
                'remote_execution_authorized': False}
    mode = context.get('mode')
    if mode not in ROUTES:
        return {'status': 'outside_scope', 'remote_execution_authorized': False}
    skill, unit = ROUTES[mode]
    errors, cautions = [], []
    project = context.get('project_ref')
    if context.get('project_state') == 'existing':
        p = (root / (project or '')).resolve()
        if not p.is_relative_to(root / '项目') or not p.is_file():
            errors.append('project_missing')
        elif not context.get('project_status_read'):
            errors.append('project_state_unread')
        else:
            body = p.read_text(encoding='utf-8-sig')
            for key in ('store', 'sku'):
                if not context.get(key) or context[key] not in body:
                    errors.append('project_identity_mismatch:' + key)
    elif context.get('project_state') != 'new' or not context.get('prior_project_search'):
        errors.append('project_recovery_missing')
    for key in ('store', 'sku', 'evidence_refs'):
        if not context.get(key):
            errors.append('missing:' + key)
    for param in context.get('parameters', []):
        if param.get('for_execution') and param.get('authority') != 'current_task_approved':
            errors.append('parameter_not_approved:' + param.get('name', 'unknown'))
    if context.get('fabricated_claims') or context.get('review_evasion'):
        errors.append('untruthful_or_evasive_action')
    if mode == 'listing':
        if set(context.get('action_domains', [])) & {'price', 'discount', 'voucher', 'promotion', 'subsidy'}:
            errors.append('COM-004_listing_price_isolation')
        if context.get('inventory') is None or not context.get('inventory_evidence'):
            errors.append('inventory_unknown')
    if mode in {'paid_traffic_diagnosis', 'weekly_review'}:
        for key in ('currency', 'timezone', 'period_start', 'period_end', 'attribution_definition'):
            if not context.get(key):errors.append('metric_scope_missing:' + key)
        if context.get('subtract_overlapping_attribution'):
            errors.append('attribution_not_additive')
    if mode == 'paid_traffic_diagnosis':
        for key in ('account_state_checked', 'sale_state_checked', 'creative_rights_checked'):
            if context.get(key) is not True:errors.append('prerequisite_unchecked:' + key)
    if context.get('retire_for_zero_orders') and not all(context.get(k) is True for k in ('window_mature', 'sample_sufficiency_reviewed', 'sale_state_checked')):
        errors.append('COM-013_014_insufficient_retirement_evidence')
    if mode == 'content_preparation' and not all(context.get(k) for k in ('product_fact_card', 'source_rights', 'production_baseline')):
        errors.append('content_evidence_or_baseline_missing')
    if mode == 'creator_outreach':
        if not context.get('campaign_brief'):errors.append('campaign_brief_missing')
        if context.get('sample_received') is True and not context.get('post_id'):
            cautions.append('sample_received_is_not_published')
        if context.get('ad_use_planned') and not all(context.get(k) for k in ('rights_scope', 'rights_expiry', 'rights_currently_valid')):
            errors.append('ad_rights_unverified')
    if mode == 'appeal_preparation' and not all(context.get(k) for k in ('current_notice', 'current_deadline_verified', 'truthful_evidence')):
        errors.append('appeal_notice_or_evidence_unverified')
    # Preparation permission never becomes remote permission, even if this field
    # claims approval. The actual action must use its task-specific executor.
    if context.get('external_action'):
        cautions.append('route_to_current_task_authorization_gate')
    return {'vault_root': str(root), 'route': skill,
            'method': 'K-COMPANY-20260924-' + unit,
            'reference': str(root / 'skill' / skill / 'references/company-manual-methods.md'),
            'status': 'blocked' if errors else 'ready_for_local_preparation',
            'errors': errors, 'cautions': cautions,
            'remote_execution_authorized': False}


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('context');a=p.parse_args()
    result=review(json.loads(Path(a.context).read_text(encoding='utf-8-sig')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(2 if result['status']=='blocked' else 0)
