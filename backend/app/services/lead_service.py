"""
Lead State Machine Service
Enforces transition rules for Service and Lease lead cycles:
- Service Lead: prospecting -> qualification -> need_analysis -> value_proposition -> decision_makers -> proposal_price -> negotiation -> register_user -> login_guide -> payment -> closed_won
- Lease Lead: prospecting -> qualification -> need_analysis -> land_verification -> feasibility -> commercial_model -> proposal -> negotiation -> agreement -> approval -> closed_won
- Any stage can transition to closed_lost.
- Closed Lost leads are NEVER deleted from DB.
"""
from typing import Optional
from fastapi import HTTPException
from app.models.leads import Lead, LeadStatus, LeadType

# Service lead transitions order
SERVICE_STAGES = [
    LeadStatus.prospecting,
    LeadStatus.qualification,
    LeadStatus.need_analysis,
    LeadStatus.value_proposition,
    LeadStatus.decision_makers,
    LeadStatus.proposal_price,
    LeadStatus.negotiation,
    LeadStatus.register_user,
    LeadStatus.login_guide,
    LeadStatus.payment,
    LeadStatus.closed_won,
]

# Lease lead transitions order
LEASE_STAGES = [
    LeadStatus.prospecting,
    LeadStatus.qualification,
    LeadStatus.need_analysis,
    LeadStatus.land_verification,
    LeadStatus.feasibility,
    LeadStatus.commercial_model,
    LeadStatus.proposal,
    LeadStatus.negotiation,
    LeadStatus.agreement,
    LeadStatus.approval,
    LeadStatus.closed_won,
]

LAND_SALE_STAGES = [
    LeadStatus.prospecting,
    LeadStatus.qualification,
    LeadStatus.land_verification,
    LeadStatus.feasibility,
    LeadStatus.proposal,
    LeadStatus.negotiation,
    LeadStatus.agreement,
    LeadStatus.approval,
    LeadStatus.closed_won,
]


def validate_transition(lead: Lead, new: LeadStatus) -> None:
    """Validate stage transition based on lead type."""
    if lead.status in [LeadStatus.closed_won, LeadStatus.closed_lost]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition lead from terminal state '{lead.status.value}'"
        )
    if new == LeadStatus.closed_lost:
        return

    # Determine stage pipeline. Existing customers skip registration and login guidance.
    is_lease = lead.type == LeadType.farm_lease
    pipeline = LEASE_STAGES if is_lease else LAND_SALE_STAGES if lead.type == LeadType.sell_land else SERVICE_STAGES
    if lead.is_opportunity and not is_lease:
        pipeline = [stage for stage in pipeline if stage not in (LeadStatus.register_user, LeadStatus.login_guide)]
    if new not in pipeline:
        raise HTTPException(
            status_code=400,
            detail=f"Stage '{new.value}' is not valid for lead type '{lead.type.value}'"
        )

    current_index = pipeline.index(lead.status) if lead.status in pipeline else -1
    next_index = pipeline.index(new)
    if next_index > current_index + 1:
        raise HTTPException(status_code=400, detail=f"Cannot skip from '{lead.status.value}' to '{new.value}'")


def transition_lead(lead: Lead, new_status: LeadStatus, lost_reason: Optional[str] = None) -> Lead:
    """Apply a validated status transition to a lead."""
    validate_transition(lead, new_status)
    lead.status = new_status
    if new_status == LeadStatus.closed_lost and lost_reason:
        lead.lost_reason = lost_reason
    return lead
