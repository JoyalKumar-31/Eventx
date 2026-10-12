"""
tools package - Exports all fest management tools
"""

from .event_tools import (
    get_all_events,
    get_event_details,
    check_schedule_clash,
    get_coordinator_created_events,
    get_event_registrations_summary
)
from .team_tools import (
    validate_team_size,
    check_registration_status,
    verify_qr_entry_pass,
    register_student_for_event,
    get_user_registrations,
    check_in_participant
)
from .judging_tools import (
    get_evaluation_rubric,
    calculate_rankings,
    get_live_event_results,
    calculate_and_record_scores,
    get_judge_assigned_events,
    resolve_event_for_judging,
    get_event_maximum_score_and_standings,
    get_event_participants_for_judging,
    get_participant_scorecard,
    get_event_criteria_and_rubrics,
    add_event_scoring_criteria,
    publish_or_finalize_event_results
)
from .analytics_tools import get_fest_analytics, get_sponsor_reports
from .cert_tools import generate_certificate_text, draft_announcement
from .profile_tools import (
    update_student_profile,
    get_student_profile,
    parse_profile_update_intent,
    normalize_year_of_study
)

__all__ = [
    "get_all_events",
    "get_event_details",
    "check_schedule_clash",
    "get_coordinator_created_events",
    "get_event_registrations_summary",
    "validate_team_size",
    "check_registration_status",
    "verify_qr_entry_pass",
    "register_student_for_event",
    "get_user_registrations",
    "check_in_participant",
    "get_evaluation_rubric",
    "calculate_rankings",
    "get_live_event_results",
    "calculate_and_record_scores",
    "get_judge_assigned_events",
    "resolve_event_for_judging",
    "get_event_maximum_score_and_standings",
    "get_event_participants_for_judging",
    "get_participant_scorecard",
    "get_event_criteria_and_rubrics",
    "add_event_scoring_criteria",
    "publish_or_finalize_event_results",
    "get_fest_analytics",
    "get_sponsor_reports",
    "generate_certificate_text",
    "draft_announcement",
    "update_student_profile",
    "get_student_profile",
    "parse_profile_update_intent",
    "normalize_year_of_study"
]
