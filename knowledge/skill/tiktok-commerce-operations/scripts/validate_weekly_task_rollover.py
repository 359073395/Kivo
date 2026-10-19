"""Read-only ten-store weekly rollover check. Never deletes or authorizes platforms.

Input: as_of (timezone-aware ISO timestamp), beijing_date, plan_start, plan_end,
snapshot_file (JSON list of pre-change records), snapshot_sha256,
archive_matches_prechange_readback, snapshot_includes_actual_fields,
removed_task_ids, active_tasks, protected_business_data_unchanged,
daily_quantities, creator_targets and plan_status=incomplete|complete.
Cross-week plans supply work_dates and rest_dates covering the exact date span.
Optional video_work_blocks must separate material_search from production;
production requires ready evidence or an explicit ready-before-production gate.
An optional remaining_day checks tool-clock timestamps at publication and delivery,
actuals readback and remaining intervals against the already fixed work end.

Records: id, date, kind=task|sales|patrol|business_record; archived actual fields
are retained in the snapshot. Rescheduled tasks set rescheduled=true and supply
source_task_id plus carry_reason. daily_quantities separates fixed targets,
eligible_new_skus, actual_new_listings (integer or null), actuals_verified,
same_batch_all_stores and old_work_counted_as_new. Checks do not prove the
truth of the caller's source evidence or the suitability of a SKU.
creator_targets preserves 3 main stores x 200/workday, 7 other stores x 200/week,
the 5000 full-six-day reference, budget_cancels_quota=false, and an explicit
partial_week_explanation when the actual plan covers fewer than six days.
"""
import argparse
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from validate_ten_store_daily_batch import targets_for_plan


def validate_remaining_day(context):
    """Check supplied clock/readback evidence, never invent completed work."""
    issues=[]
    try:
        def parsed(value):
            result=datetime.fromisoformat(value)
            if result.tzinfo is None:raise ValueError('timezone absent')
            return result.astimezone(timezone(timedelta(hours=8)))
        planned=parsed(context['planned_at']);published=parsed(context['publish_checked_at'])
        delivered=parsed(context['delivery_checked_at'])
        work_end=parsed(context['fixed_work_end'])
        if planned.date()!=published.date() or delivered.date()!=published.date() or work_end.date()!=published.date() or published<planned or delivered<published:
            issues.append('remaining_day_clock_or_date_invalid')
        intervals=[(parsed(row['start']),parsed(row['end'])) for row in context['remaining_tasks']]
        scheduled=0
        previous_end=delivered
        for start,end in sorted(intervals):
            if start<published:issues.append('elapsed_slot_cannot_remain_active_at_publication')
            if start<delivered:issues.append('elapsed_slot_cannot_remain_active_at_delivery')
            if end>work_end:issues.append('remaining_day_exceeds_fixed_work_end')
            if start<previous_end or end<=start:issues.append('remaining_day_interval_invalid_or_overlapping')
            previous_end=end;scheduled+=(end-start).total_seconds()/60
    except (KeyError,TypeError,ValueError):
        return {'passed':False,'issues':['remaining_day_time_context_invalid']}
    if context.get('clock_source')!='tool':issues.append('current_beijing_time_requires_tool_read')
    if context.get('actuals_readback_performed') is not True:issues.append('today_actuals_must_be_read_before_rescheduling')
    if context.get('unknown_actuals_kept_unknown') is not True:issues.append('unknown_actuals_cannot_be_zero_or_backfilled')
    if context.get('automatic_debt_carryover') is not False:issues.append('today_debt_cannot_automatically_stack_tomorrow')
    actual=context.get('actual_completed')
    if actual is not None and context.get('actuals_verified') is not True:
        issues.append('remaining_day_actuals_unverified')
    return {'passed':not issues,'issues':issues,
            'available_minutes_at_publish':max(0,(work_end-published).total_seconds()/60),
            'available_minutes_at_delivery':max(0,(work_end-delivered).total_seconds()/60),
            'scheduled_minutes':scheduled,'actual_completed':actual,
            'full_day_budget_not_available_again':True}


def assess_current_manual_capacity():
    """Use current daily estimates; derived unit budgets are not measured time."""
    standard=json.loads((Path(__file__).resolve().parents[1]/'references'/'ten-store-daily-test-standard.json').read_text(encoding='utf-8'))
    timing=standard['daily_capacity_user_timing']
    skus=timing.get('quantity_basis_daily_unique_skus',standard['daily_unique_skus'])
    material=timing['daily_material_minutes']
    listing=timing['daily_listing_minutes']
    creator=standard['creator_invitation_targets']
    invite_minutes=creator['manual_200_minutes']/200
    main_daily=creator['main_store_count']*creator['per_main_store_per_workday']*invite_minutes
    weekly_invites=creator['full_six_workday_week_total']*invite_minutes
    workdays=timing['workdays_per_week']
    weekly_core=(material+listing)*workdays
    daily_work=timing['work_minutes_per_day']
    return {'material_minutes_once_for_all_stores':material,
            'listing_minutes_all_ten_stores':listing,
            'two_task_minutes':material+listing,
            'work_minutes_per_day':daily_work,
            'remaining_after_two_tasks':daily_work-material-listing,
            'main_daily_pure_invitation_minutes':main_daily,
            'remaining_after_core_and_main_invites':daily_work-material-listing-main_daily,
            'full_week_pure_invitation_minutes':weekly_invites,
            'full_week_core_and_pure_invites':weekly_core+weekly_invites,
            'full_week_budget_minutes':daily_work*workdays,
            'other_work_included':False,
            'two_tasks_fit_workday':material+listing<=daily_work,
            'full_schedule_verified':timing['full_schedule_verified'],
            'cross_task_overlap_verified':timing['cross_task_overlap_verified'],
            'derived_minutes_per_material_set':material/(skus*standard['initial_versions_per_sku']),
            'derived_minutes_per_sku_all_stores':listing/skus,
            'derived_unit_rates_are_measured':False,
            'video_material_search_requires_separate_block':True,
            'video_production_requires_separate_block':True,
            'basis':timing['basis'],
            'budget_applicability':timing.get('applicability','current_project'),
            'budget_quantity_basis_daily_unique_skus':skus,
            'current_target_daily_unique_skus':standard['daily_unique_skus'],
            'morning_capacity_feedback':standard.get('morning_capacity_feedback')}


def validate(payload):
    issues=[]
    try:
        observed=datetime.fromisoformat(payload['as_of'])
        if observed.tzinfo is None:raise ValueError('timezone absent')
        today=observed.astimezone(timezone(timedelta(hours=8))).date()
        start=date.fromisoformat(payload['plan_start']);end=date.fromisoformat(payload['plan_end'])
        if payload.get('beijing_date')!=today.isoformat():issues.append('beijing_date_not_restored')
        if start>end:issues.append('actual_plan_date_range_invalid')
        if start<today:issues.append('active_plan_starts_before_current_beijing_date')
    except (KeyError,ValueError,TypeError):
        return {'passed':False,'issues':['invalid_date_context'],'can_mark_plan_complete':False}
    try:
        raw=Path(payload['snapshot_file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=payload.get('snapshot_sha256'):raise ValueError('hash mismatch')
        archived=json.loads(raw)
        if not isinstance(archived,list):raise ValueError('not record list')
    except (KeyError,ValueError,TypeError,OSError):
        archived=[];issues.append('local_snapshot_missing_unreadable_or_hash_mismatch')
    if payload.get('archive_matches_prechange_readback') is not True:issues.append('archive_not_verified_against_original')
    if payload.get('snapshot_includes_actual_fields') is not True:issues.append('actuals_not_preserved_in_archive')
    by_id={r.get('id'):r for r in archived}
    if len(by_id)!=len(archived):issues.append('ambiguous_source_record_ids')
    removed=set(payload.get('removed_task_ids',[]))
    for ident in removed:
        row=by_id.get(ident)
        if not row:issues.append('removed_task_not_archived:'+str(ident));continue
        if row.get('kind')!='task':issues.append('non_task_business_record_deleted:'+str(ident));continue
        if row.get('date','')>=start.isoformat():issues.append('current_or_future_task_deleted:'+str(ident))
    expired={r.get('id') for r in archived if r.get('kind')=='task' and r.get('date','')<start.isoformat()}
    if expired-removed:issues.append('old_tasks_not_removed_from_execution_area')
    for row in payload.get('active_tasks',[]):
        if row.get('kind','task')!='task':continue
        try:task_date=date.fromisoformat(row['date'])
        except (KeyError,ValueError,TypeError):issues.append('active_task_date_invalid');continue
        if task_date<start:issues.append('old_date_task_still_active:'+str(row.get('id')))
        if row.get('rescheduled'):
            source=by_id.get(row.get('source_task_id'))
            if not source or source.get('kind')!='task' or not row.get('carry_reason'):
                issues.append('unfinished_carryover_missing_source_or_reason')
    if payload.get('protected_business_data_unchanged') is not True:issues.append('sales_patrol_or_non_task_data_not_protected')
    quantities=payload.get('daily_quantities',[])
    dates=[r.get('date') for r in quantities]
    calendar_dates=[(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    explicit_work_dates=payload.get('work_dates')
    if explicit_work_dates is None:
        required_dates=calendar_dates
        if start.isocalendar()[:2]!=end.isocalendar()[:2]:issues.append('cross_week_plan_requires_explicit_work_and_rest_dates')
    else:
        required_dates=explicit_work_dates
        rest_dates=payload.get('rest_dates',[])
        if (not isinstance(required_dates,list) or not isinstance(rest_dates,list)
                or any(not isinstance(d,str) for d in required_dates+rest_dates)):
            required_dates=[];rest_dates=[];issues.append('work_and_rest_dates_invalid')
        if (len(required_dates)!=len(set(required_dates)) or len(rest_dates)!=len(set(rest_dates))
                or set(required_dates)&set(rest_dates) or sorted(required_dates+rest_dates)!=calendar_dates):
            issues.append('work_and_rest_dates_must_partition_plan_range')
        weeks={date.fromisoformat(d).isocalendar()[:2] for d in calendar_dates}
        if any(sum(date.fromisoformat(d).isocalendar()[:2]==week for d in required_dates if d in calendar_dates)>6 for week in weeks):
            issues.append('more_than_six_workdays_in_iso_week')
    if sorted(dates)!=required_dates:issues.append('daily_quantity_coverage_incomplete_or_duplicate')
    incomplete=[]
    actuals=[]
    plan_skus=set()
    standard=json.loads((Path(__file__).resolve().parents[1]/'references'/'ten-store-daily-test-standard.json').read_text(encoding='utf-8-sig'))
    targets=targets_for_plan(standard,today.isoformat())
    target_count=targets['daily_unique_skus']
    for row in quantities:
        if any(row.get(k)!=v for k,v in [('target_unique_skus',target_count),('target_per_store_skus',targets['daily_per_store_skus']),('target_total_listings',targets['daily_total_listing_target']),('initial_versions_per_sku',standard['initial_versions_per_sku'])]):
            issues.append('strict_quantity_target_changed:'+str(row.get('date')))
        if row.get('same_batch_all_stores') is not True:issues.append('ten_store_same_batch_not_verified')
        skus=row.get('eligible_new_skus',[])
        if len(skus)!=len(set(skus)) or any(not isinstance(s,str) or not s.strip() for s in skus):
            issues.append('duplicate_versions_or_placeholder_counted_as_unique_skus')
        if plan_skus.intersection(skus):issues.append('same_sku_repeated_across_days_not_new_unique_sku')
        plan_skus.update(skus)
        if len(set(skus))<target_count:incomplete.append(row.get('date'))
        if row.get('old_work_counted_as_new') is not False:issues.append('old_link_work_counted_as_new_or_unverified')
        actual=row.get('actual_new_listings')
        if actual is not None and (type(actual) is not int or actual<0 or row.get('actuals_verified') is not True):
            issues.append('planned_quantity_or_unverified_value_used_as_actual')
        actuals.append({'date':row.get('date'),'actual_new_listings':actual})
    creator=payload.get('creator_targets',{})
    required_creator={'main_store_count':3,'per_main_store_per_workday':200,
                      'other_store_count':7,'per_other_store_per_week':200,
                      'full_six_workday_week_total':5000}
    if any(creator.get(k)!=v for k,v in required_creator.items()):
        issues.append('creator_user_quantity_missing_cancelled_or_reduced')
    if creator.get('budget_cancels_quota') is not False:
        issues.append('ai_time_budget_cannot_cancel_creator_quota')
    workday_weeks={date.fromisoformat(d).isocalendar()[:2] for d in required_dates if d in calendar_dates}
    has_partial_week=any(sum(date.fromisoformat(d).isocalendar()[:2]==week for d in required_dates if d in calendar_dates)<6 for week in workday_weeks)
    if has_partial_week and not creator.get('partial_week_explanation'):
        issues.append('partial_week_creator_target_needs_explicit_workdays_and_rotation')
    video_blocks=payload.get('video_work_blocks',[])
    if video_blocks or payload.get('plan_status')=='complete':
        kinds={b.get('kind') for b in video_blocks}
        if not {'material_search','production'}.issubset(kinds):
            issues.append('video_search_and_production_require_separate_blocks')
        for block in video_blocks:
            if block.get('kind')!='production':continue
            if block.get('assets_ready') is True and not block.get('readiness_evidence'):
                issues.append('video_assets_claimed_ready_without_evidence')
            elif block.get('assets_ready') is not True and block.get('requires_ready_before_production') is not True:
                issues.append('video_production_requires_ready_materials_gate')
    if payload.get('plan_status') not in ('incomplete','complete'):issues.append('plan_status_missing')
    if incomplete and payload.get('plan_status')=='complete':issues.append('quantity_gap_cannot_be_marked_complete')
    capacity=assess_current_manual_capacity()
    remaining=None
    if 'remaining_day' in payload:
        remaining=validate_remaining_day(payload['remaining_day']);issues.extend(remaining['issues'])
    if not capacity['full_schedule_verified'] and payload.get('plan_status')=='complete':
        issues.append('full_schedule_unverified_cannot_claim_executable_plan')
    return {'passed':not issues,'issues':issues,'incomplete_dates':incomplete,
            'can_mark_plan_complete':not issues and not incomplete and capacity['full_schedule_verified'],
            'actuals':actuals,'capacity_review':capacity,'remaining_day_review':remaining,'quantity_targets':targets,
            'platform_actions_authorized':False,'business_effect_verified':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);args=parser.parse_args()
    result=validate(json.loads(args.input.read_text(encoding='utf-8-sig')))
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['passed'] else 1)
