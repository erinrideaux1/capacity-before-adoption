"""Privacy-minimal, deterministic longitudinal HR discovery summary."""

def make_longitudinal_brief(periods):
    b,a=periods['before'],periods['after']
    measures=(
        ('Recorded unavailable days/week','recorded_leave_days_per_week'),
        ('Recorded break days/week','recorded_break_days_per_week'),
        ('After-hours calendar work hours/week','after_hours_per_week'),
    )
    observations=[f'{name}: {b[key]:.2f} before; {a[key]:.2f} after.' for name,key in measures]
    observations.append(f"Recorded work overlapping unavailable blocks: {b['work_during_recorded_leave_hours']:.2f} hours before; {a['work_during_recorded_leave_hours']:.2f} hours after (period totals, not weekly rates).")
    return {'observations':observations,
      'uncertainties':['Calendar labels and attendance are unverified; unrecorded breaks, leave, and work are not visible.',
                       'A before/after change does not establish that the new AI expectation caused it or that health was affected.'],
      'discovery_questions':['Have work expectations or other conditions changed how you protect breaks, leave, and personal time?',
                             'Is any recorded work during unavailable time an invitation conflict, rescheduled leave, or actual work?',
                             'What workload changes or organizational support would make AI development sustainable?'],
      'handoff':'Discuss these aggregate signals privately with the leader. Do not infer medical status, sick-leave appropriateness, motivation, or individual performance.'}
