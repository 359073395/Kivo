"""Synthetic failure cases for task cleanup and strict quantities; no cloud calls."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_weekly_task_rollover import validate,assess_current_manual_capacity,validate_remaining_day


class RolloverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.snapshot=Path(self.tmp.name)/'snapshot.json'
        rows=[{'id':'old-task','date':'2026-10-07','kind':'task','actuals':{'invites':17,'note':'preserved'}},
              {'id':'sales','date':'2026-09-27','kind':'sales','orders':200}]
        self.snapshot.write_text(json.dumps(rows),encoding='utf-8')
    def base(self):
        quantities=[]
        for dt in ['2026-10-08','2026-10-09','2026-10-10']:
            quantities.append(dict(date=dt,target_unique_skus=10,target_per_store_skus=10,target_total_listings=100,initial_versions_per_sku=1,
                eligible_new_skus=[dt+'-sku-'+str(i) for i in range(10)],same_batch_all_stores=True,old_work_counted_as_new=False,actual_new_listings=None,actuals_verified=False))
        return dict(as_of='2026-10-07T17:00:00+00:00',beijing_date='2026-10-08',plan_start='2026-10-08',plan_end='2026-10-10',
            snapshot_file=str(self.snapshot),snapshot_sha256=hashlib.sha256(self.snapshot.read_bytes()).hexdigest(),archive_matches_prechange_readback=True,
            snapshot_includes_actual_fields=True,removed_task_ids=['old-task'],active_tasks=[dict(id='new-task',date='2026-10-08',kind='task')],
            protected_business_data_unchanged=True,daily_quantities=quantities,plan_status='incomplete',
            creator_targets=dict(main_store_count=3,per_main_store_per_workday=200,other_store_count=7,
                per_other_store_per_week=200,full_six_workday_week_total=5000,budget_cancels_quota=False,
                partial_week_explanation='3 actual workdays; retain main-store daily quota and explicitly schedule all seven weekly rotations, not 5000 actual invites'))
    def test_correct_rollover_keeps_unknown_actuals(self):
        r=validate(self.base());self.assertTrue(r['passed']);self.assertTrue(all(x['actual_new_listings'] is None for x in r['actuals']))
    def new_five_plan(self):
        p=self.base();p.update(as_of='2026-10-16T08:00:00+08:00',beijing_date='2026-10-16',plan_start='2026-10-16',plan_end='2026-10-17')
        p['active_tasks'][0]['date']='2026-10-16';p['daily_quantities']=p['daily_quantities'][:2]
        for row,dt in zip(p['daily_quantities'],['2026-10-16','2026-10-17']):
            row.update(date=dt,target_unique_skus=5,target_per_store_skus=5,target_total_listings=50,eligible_new_skus=[dt+'-sku-'+str(i) for i in range(5)])
        return p
    def test_next_plan_uses_five_without_rewriting_published_history(self):
        p=self.new_five_plan();r=validate(p);self.assertTrue(r['passed']);self.assertEqual(r['quantity_targets']['daily_total_listing_target'],50)
        self.assertTrue(validate(self.extended_plan())['passed'])
        self.assertTrue(all(x['actual_new_listings'] is None for x in r['actuals']))
    def test_next_plan_cannot_restore_ten_or_fabricate_fifty_actuals(self):
        p=self.new_five_plan();p['daily_quantities'][0]['target_unique_skus']=10;self.assertFalse(validate(p)['passed'])
        p=self.new_five_plan();p['daily_quantities'][0]['actual_new_listings']=50;self.assertFalse(validate(p)['passed'])
    def test_old_240_120_budget_not_implicitly_redivided_by_five(self):
        c=assess_current_manual_capacity();self.assertEqual(c['budget_quantity_basis_daily_unique_skus'],10)
        self.assertEqual(c['current_target_daily_unique_skus'],5);self.assertIn('historical',c['budget_applicability'])
        self.assertIsNone(c['morning_capacity_feedback']['elapsed_minutes'])
    def test_beijing_date_not_utc_date(self):
        p=self.base();p['beijing_date']='2026-10-07';self.assertFalse(validate(p)['passed'])
    def test_title_only_change_cannot_leave_old_rows(self):
        p=self.base();p['removed_task_ids']=[];p['active_tasks'][0].update(date='2026-10-07',status='未开始');self.assertFalse(validate(p)['passed'])
    def test_archive_missing_or_tampered_blocks_cleanup(self):
        p=self.base();p['snapshot_sha256']='0'*64;self.assertFalse(validate(p)['passed'])
    def test_actuals_must_be_archived(self):
        p=self.base();p['snapshot_includes_actual_fields']=False;self.assertFalse(validate(p)['passed'])
    def test_never_remove_raw_sales(self):
        p=self.base();p['removed_task_ids'].append('sales');self.assertFalse(validate(p)['passed'])
    def test_reschedule_requires_explicit_source_and_reason(self):
        p=self.base();p['active_tasks'][0]['rescheduled']=True;self.assertFalse(validate(p)['passed'])
        p['active_tasks'][0].update(source_task_id='old-task',carry_reason='reply remains necessary in current capacity');self.assertTrue(validate(p)['passed'])
    def test_five_candidates_do_not_complete_30_sku_plan(self):
        p=self.base();p['plan_status']='complete'
        for row,n in zip(p['daily_quantities'],[2,2,1]):row['eligible_new_skus']=row['eligible_new_skus'][:n]
        self.assertFalse(validate(p)['passed']);p['plan_status']='incomplete';r=validate(p);self.assertTrue(r['passed']);self.assertFalse(r['can_mark_plan_complete'])
    def test_targets_cannot_be_silently_reduced(self):
        p=self.base();p['daily_quantities'][0]['target_unique_skus']=2;self.assertFalse(validate(p)['passed'])
    def test_duplicate_versions_and_old_link_optimization_do_not_count(self):
        p=self.base();p['daily_quantities'][0]['eligible_new_skus']=['same-sku']*10;self.assertFalse(validate(p)['passed'])
        p=self.base();p['daily_quantities'][0]['old_work_counted_as_new']=True;self.assertFalse(validate(p)['passed'])
    def test_plan_100_is_not_actual_100(self):
        p=self.base();p['daily_quantities'][0]['actual_new_listings']=100;self.assertFalse(validate(p)['passed'])
    def test_readback_business_data_protection_required(self):
        p=self.base();p['protected_business_data_unchanged']=False;self.assertFalse(validate(p)['passed'])
    def test_ai_90_minute_budget_cannot_cancel_user_5000_quota(self):
        p=self.base();p['creator_targets']['budget_cancels_quota']=True;self.assertFalse(validate(p)['passed'])
        p=self.base();p['creator_targets']['full_six_workday_week_total']=0;self.assertFalse(validate(p)['passed'])
    def test_partial_week_creator_targets_need_workday_and_rotation_explanation(self):
        p=self.base();del p['creator_targets']['partial_week_explanation'];self.assertFalse(validate(p)['passed'])
    def test_materials_shared_once_not_ten_copies(self):
        c=assess_current_manual_capacity();self.assertEqual(c['material_minutes_once_for_all_stores'],240)
    def test_daily_upload_budget_is_not_old_unit_time_or_divided_again(self):
        c=assess_current_manual_capacity();self.assertEqual(c['listing_minutes_all_ten_stores'],120)
        self.assertNotEqual(c['listing_minutes_all_ten_stores'],24)
        self.assertEqual(c['two_task_minutes'],360);self.assertEqual(c['work_minutes_per_day'],600)
        self.assertTrue(c['two_tasks_fit_workday']);self.assertFalse(c['other_work_included'])
        self.assertEqual(c['derived_minutes_per_material_set'],24)
        self.assertEqual(c['derived_minutes_per_sku_all_stores'],12)
        self.assertFalse(c['derived_unit_rates_are_measured'])
        self.assertEqual(c['basis'],'user_estimated_daily_total_plan_budget_not_measured')
    def test_remaining_minutes_do_not_remove_creator_or_other_work(self):
        c=assess_current_manual_capacity();self.assertEqual(c['remaining_after_two_tasks'],240)
        self.assertEqual(c['main_daily_pure_invitation_minutes'],90)
        self.assertEqual(c['remaining_after_core_and_main_invites'],150)
        self.assertEqual(c['full_week_pure_invitation_minutes'],750)
        self.assertEqual(c['full_week_core_and_pure_invites'],2910)
        self.assertEqual(c['full_week_budget_minutes'],3600)
        self.assertFalse(c['cross_task_overlap_verified']);self.assertFalse(c['full_schedule_verified'])
    def test_complete_quantities_and_360_core_minutes_do_not_prove_full_10h_plan(self):
        p=self.base();p['plan_status']='complete';r=validate(p)
        self.assertFalse(r['passed']);self.assertFalse(r['can_mark_plan_complete'])
        self.assertIn('full_schedule_unverified_cannot_claim_executable_plan',r['issues'])
    def test_video_material_search_and_production_cannot_be_one_block(self):
        p=self.base();p['video_work_blocks']=[dict(kind='search_and_produce')]
        self.assertIn('video_search_and_production_require_separate_blocks',validate(p)['issues'])
    def test_unknown_video_materials_require_readiness_gate_not_invented_assets(self):
        p=self.base();p['video_work_blocks']=[dict(kind='material_search'),dict(kind='production',assets_ready=False)]
        self.assertIn('video_production_requires_ready_materials_gate',validate(p)['issues'])
        p['video_work_blocks'][1]['requires_ready_before_production']=True
        self.assertTrue(validate(p)['passed'])
        p['video_work_blocks'][1]['assets_ready']=True
        self.assertIn('video_assets_claimed_ready_without_evidence',validate(p)['issues'])
    def extended_plan(self):
        p=self.base();p['plan_end']='2026-10-17'
        p['work_dates']=['2026-10-'+format(i,'02d') for i in [8,9,10,12,13,14,15,16,17]]
        p['rest_dates']=['2026-10-11']
        first=copy.deepcopy(p['daily_quantities'][0]);p['daily_quantities']=[]
        for dt in p['work_dates']:
            row=copy.deepcopy(first);row['date']=dt;row['eligible_new_skus']=[dt+'-sku-'+str(i) for i in range(10)]
            p['daily_quantities'].append(row)
        return p
    def test_user_range_to_17_has_nine_workdays_and_sunday_rest(self):
        p=self.extended_plan();r=validate(p);self.assertTrue(r['passed'])
        self.assertEqual(sum(x['target_unique_skus'] for x in p['daily_quantities']),90)
        self.assertEqual(sum(x['target_total_listings'] for x in p['daily_quantities']),900)
        self.assertTrue(all(x['actual_new_listings'] is None for x in r['actuals']))
    def test_cross_week_plan_needs_exact_workday_partition(self):
        p=self.extended_plan();p['work_dates'].append('2026-10-11')
        self.assertFalse(validate(p)['passed'])
        p=self.extended_plan();del p['work_dates'];del p['rest_dates']
        self.assertIn('cross_week_plan_requires_explicit_work_and_rest_dates',validate(p)['issues'])
    def test_cross_week_partial_week_is_not_hidden_by_nine_day_total(self):
        p=self.extended_plan();del p['creator_targets']['partial_week_explanation']
        self.assertIn('partial_week_creator_target_needs_explicit_workdays_and_rotation',validate(p)['issues'])
    def test_same_sku_across_days_cannot_fill_90_unique_new_sku_target(self):
        p=self.extended_plan();p['daily_quantities'][3]['eligible_new_skus']=p['daily_quantities'][0]['eligible_new_skus'][:]
        self.assertIn('same_sku_repeated_across_days_not_new_unique_sku',validate(p)['issues'])
    def remaining_day(self):
        return dict(planned_at='2026-10-08T13:57:17+08:00',publish_checked_at='2026-10-08T14:05:00+08:00',
            delivery_checked_at='2026-10-08T14:08:00+08:00',
            fixed_work_end='2026-10-08T19:30:00+08:00',clock_source='tool',actuals_readback_performed=True,
            unknown_actuals_kept_unknown=True,actual_completed=None,actuals_verified=False,automatic_debt_carryover=False,
            remaining_tasks=[dict(start='2026-10-08T14:10:00+08:00',end='2026-10-08T19:30:00+08:00')])
    def test_remaining_day_uses_publish_clock_and_preserves_unknown_actuals(self):
        r=validate_remaining_day(self.remaining_day());self.assertTrue(r['passed'])
        self.assertEqual(r['available_minutes_at_publish'],325);self.assertEqual(r['scheduled_minutes'],320)
        self.assertEqual(r['available_minutes_at_delivery'],322)
        self.assertIsNone(r['actual_completed'])
    def test_elapsed_first_slot_and_overtime_cannot_pass_after_delayed_publish(self):
        c=self.remaining_day();c['delivery_checked_at']='2026-10-08T14:12:00+08:00'
        c['remaining_tasks'][0]['end']='2026-10-08T19:35:00+08:00'
        r=validate_remaining_day(c);self.assertFalse(r['passed'])
        self.assertIn('elapsed_slot_cannot_remain_active_at_delivery',r['issues'])
        self.assertIn('remaining_day_exceeds_fixed_work_end',r['issues'])

if __name__=='__main__':unittest.main(verbosity=2)
