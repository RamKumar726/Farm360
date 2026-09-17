# Import all models so SQLAlchemy can resolve relationships and Alembic can detect them
from app.models.users import User, UserRole
from app.models.branches import Branch
from app.models.zones import Zone
from app.models.leads import Lead, LeadType, LeadSource, LeadStatus
from app.models.customers import Customer, ServiceType
from app.models.farms import Farm
from app.models.agreements import Agreement, AgreementType, AgreementStatus
from app.models.work_orders import WorkOrder, WorkOrderType, WorkOrderStatus, PaymentStatus
from app.models.visits import Visit, VisitType, VisitStatus
from app.models.work_partners import WorkPartner, WorkPartnerStatus
from app.models.land_sales import LandSale, LandType, LandSaleStatus
from app.models.investments import Investment, InvestmentType, InvestmentStatus
from app.models.projects import Project, ProjectType, ProjectStatus
from app.models.brokers import Broker
from app.models.prescriptions import Prescription, PrescriptionStatus
from app.models.crop_designs import CropDesign, ApprovalStatus
from app.models.crop_cycles import CropCycle
from app.models.notifications import Notification, NotificationType, NotificationChannel
from app.models.attendance import Attendance, AttendanceStatus
from app.models.real_estate_users import RealEstateUser, RegistrationStatus

__all__ = [
    "User", "UserRole",
    "Branch",
    "Zone",
    "Lead", "LeadType", "LeadSource", "LeadStatus",
    "Customer", "ServiceType",
    "Farm",
    "Agreement", "AgreementType", "AgreementStatus",
    "WorkOrder", "WorkOrderType", "WorkOrderStatus", "PaymentStatus",
    "Visit", "VisitType", "VisitStatus",
    "WorkPartner", "WorkPartnerStatus",
    "LandSale", "LandType", "LandSaleStatus",
    "Investment", "InvestmentType", "InvestmentStatus",
    "Project", "ProjectType", "ProjectStatus",
    "Broker",
    "Prescription", "PrescriptionStatus",
    "CropDesign", "ApprovalStatus",
    "CropCycle",
    "Notification", "NotificationType", "NotificationChannel",
    "Attendance", "AttendanceStatus",
    "RealEstateUser", "RegistrationStatus",
]
