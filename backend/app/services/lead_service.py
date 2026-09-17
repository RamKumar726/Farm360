"""
Lead State Machine Service
Enforces the strict transition rules:
  new → site_visit → advance_paid → won → completed
  Any stage → lost (terminal)
  Lost leads are NEVER deleted from DB.
"""
from typing import Optional
from fastapi import HTTPException
from app.models.leads import Lead, LeadStatus

# Valid transitions map
VALID_TRANSITIONS = {
    LeadStatus.new: [LeadStatus.site_visit, LeadStatus.lost],
    LeadStatus.site_visit: [LeadStatus.advance_paid, LeadStatus.lost],
    LeadStatus.advance_paid: [LeadStatus.won, LeadStatus.lost],
    LeadStatus.won: [LeadStatus.completed, LeadStatus.lost],
    LeadStatus.completed: [],       # terminal success state
    LeadStatus.lost: [],            # terminal — no more transitions
}


def validate_transition(current: LeadStatus, new: LeadStatus) -> None:
    """Raise HTTPException if the transition is not allowed."""
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid lead status transition: '{current.value}' → '{new.value}'. "
                f"Allowed: {[s.value for s in allowed] or 'none (terminal state)'}"
            ),
        )


def transition_lead(lead: Lead, new_status: LeadStatus, lost_reason: Optional[str] = None) -> Lead:
    """Apply a validated status transition to a lead."""
    validate_transition(lead.status, new_status)
    lead.status = new_status
    if new_status == LeadStatus.lost and lost_reason:
        lead.lost_reason = lost_reason
    return lead
