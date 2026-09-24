import uuid
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
import app.models  # Load all models
from app.models.users import User, UserRole
from app.models.branches import Branch
from app.models.zones import Zone
from app.models.customers import Customer, ServiceType
from app.models.farms import Farm
from app.models.leads import Lead, LeadStatus, LeadSource, LeadType
from app.models.work_orders import WorkOrder, WorkOrderStatus, WorkOrderType, PaymentStatus
from app.models.visits import Visit, VisitType, VisitStatus
from app.models.prescriptions import Prescription, PrescriptionStatus
from app.models.crop_designs import CropDesign, ApprovalStatus
from app.models.land_sales import LandSale, LandType, LandSaleStatus
from app.models.investments import Investment, InvestmentType, InvestmentStatus
from app.models.projects import Project, ProjectStatus, ProjectType
from app.auth.jwt import hash_password


def seed_database():
    print("Initializing & Seeding Enterprise Database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        from sqlalchemy import text
        try:
            db.execute(text("UPDATE leads SET status = 'prospecting' WHERE status IN ('site_visit', 'new');"))
            db.execute(text("UPDATE leads SET status = 'closed_won' WHERE status = 'won';"))
            db.execute(text("UPDATE leads SET status = 'closed_lost' WHERE status = 'lost';"))
            db.commit()
        except Exception as e:
            print(f"SQL Cleanup Notice: {e}")
            db.rollback()
        # --- 1. BRANCHES ---
        branch_configs = [
            {"name": "Rajahmundry Main Branch", "location": "NH-16, Rajahmundry, East Godavari, AP"},
            {"name": "Visakhapatnam Coastal Branch", "location": "Beach Road, Visakhapatnam, AP"},
            {"name": "Vijayawada Central Branch", "location": "MG Road, Vijayawada, AP"},
            {"name": "Hyderabad Tech AgHub Branch", "location": "HITEC City, Hyderabad, TS"},
        ]
        branches = {}
        for b_cfg in branch_configs:
            obj = db.query(Branch).filter(Branch.name == b_cfg["name"]).first()
            if not obj:
                obj = Branch(id=str(uuid.uuid4()), name=b_cfg["name"], location=b_cfg["location"])
                db.add(obj)
                db.commit()
                db.refresh(obj)
            branches[b_cfg["name"]] = obj
        print(f"Created/Verified {len(branches)} Branches")

        rjy_branch = branches["Rajahmundry Main Branch"]
        vzg_branch = branches["Visakhapatnam Coastal Branch"]
        vij_branch = branches["Vijayawada Central Branch"]
        hyd_branch = branches["Hyderabad Tech AgHub Branch"]

        # --- 2. ZONES ---
        zone_configs = [
            {"name": "East Godavari Zone A (Delta)", "branch_id": rjy_branch.id},
            {"name": "West Godavari Zone B (River Basin)", "branch_id": rjy_branch.id},
            {"name": "Vizag North Coastal Zone", "branch_id": vzg_branch.id},
            {"name": "Guntur-Vijayawada Chili & Paddy Zone", "branch_id": vij_branch.id},
            {"name": "Cyberabad Precision Farm Zone", "branch_id": hyd_branch.id},
        ]
        zones = {}
        for z_cfg in zone_configs:
            obj = db.query(Zone).filter(Zone.name == z_cfg["name"]).first()
            if not obj:
                obj = Zone(id=str(uuid.uuid4()), name=z_cfg["name"], branch_id=z_cfg["branch_id"])
                db.add(obj)
                db.commit()
                db.refresh(obj)
            zones[z_cfg["name"]] = obj
        print(f"Created/Verified {len(zones)} Zones")

        eg_zone = zones["East Godavari Zone A (Delta)"]
        vzg_zone = zones["Vizag North Coastal Zone"]

        # --- 3. USERS ---
        pwd_hash = hash_password("password123")
        users_data = [
            {"email": "founder@prasadfarm.com", "name": "Prasad Founder (CEO)", "role": UserRole.founder, "phone": "+91 98765 00001"},
            {"email": "zoneadmin@prasadfarm.com", "name": "Rajesh (Rajahmundry Admin)", "role": UserRole.zone_admin, "phone": "+91 98765 00002", "branch_id": rjy_branch.id, "zone_id": eg_zone.id},
            {"email": "vizag.admin@prasadfarm.com", "name": "Lakshmi (Vizag Admin)", "role": UserRole.zone_admin, "phone": "+91 98765 00003", "branch_id": vzg_branch.id, "zone_id": vzg_zone.id},
            {"email": "employee@prasadfarm.com", "name": "Suresh CRM Executive", "role": UserRole.employee, "phone": "+91 98765 00004", "branch_id": rjy_branch.id, "zone_id": eg_zone.id},
            {"email": "sita.employee@prasadfarm.com", "name": "Sita Lead Coordinator", "role": UserRole.employee, "phone": "+91 98765 00005", "branch_id": vzg_branch.id, "zone_id": vzg_zone.id},
            {"email": "agriofficer@prasadfarm.com", "name": "Dr. Ramesh (Chief Agronomist)", "role": UserRole.agri_officer, "phone": "+91 98765 00006", "branch_id": rjy_branch.id},
            {"email": "agri.anand@prasadfarm.com", "name": "Dr. Anand Soil Specialist", "role": UserRole.agri_officer, "phone": "+91 98765 00007", "branch_id": vzg_branch.id},
            {"email": "farmemployee@prasadfarm.com", "name": "Venkatesh Field Agent", "role": UserRole.farm_employee, "phone": "+91 98765 00008", "branch_id": rjy_branch.id, "zone_id": eg_zone.id},
            {"email": "field.kiran@prasadfarm.com", "name": "Kiran Field Inspector", "role": UserRole.farm_employee, "phone": "+91 98765 00009", "branch_id": vzg_branch.id, "zone_id": vzg_zone.id},
            {"email": "customer@prasadfarm.com", "name": "Ravi Teja (Farm Owner)", "role": UserRole.customer, "phone": "+91 98765 00010"},
            {"email": "customer.anil@prasadfarm.com", "name": "Anil Kumar (Land Investor)", "role": UserRole.customer, "phone": "+91 98765 00011"},
            {"email": "broker.raju@prasadfarm.com", "name": "Raju (Senior Broker)", "role": UserRole.broker, "phone": "+91 98765 00012"},
        ]

        users = {}
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                existing = User(
                    id=str(uuid.uuid4()), name=u["name"], email=u["email"], phone=u.get("phone"),
                    password_hash=pwd_hash, role=u["role"], branch_id=u.get("branch_id"), zone_id=u.get("zone_id")
                )
                db.add(existing)
                db.commit()
                db.refresh(existing)
            else:
                existing.password_hash = pwd_hash
                existing.branch_id = u.get("branch_id")
                existing.zone_id = u.get("zone_id")
                existing.is_deleted = False
                db.commit()
            users[u["email"]] = existing
        print(f"Created/Verified {len(users)} Enterprise Users")

        # Update Branch & Zone Pointers
        rjy_branch.admin_user_id = users["zoneadmin@prasadfarm.com"].id
        vzg_branch.admin_user_id = users["vizag.admin@prasadfarm.com"].id
        eg_zone.responsible_employee_id = users["zoneadmin@prasadfarm.com"].id
        vzg_zone.responsible_employee_id = users["vizag.admin@prasadfarm.com"].id
        db.commit()

        # --- 4. CUSTOMERS & FARMS ---
        cust_ravi_usr = users["customer@prasadfarm.com"]
        c_ravi = db.query(Customer).filter(Customer.user_id == cust_ravi_usr.id).first()
        if not c_ravi:
            c_ravi = Customer(id=str(uuid.uuid4()), user_id=cust_ravi_usr.id, service_type=ServiceType.managed, branch_id=rjy_branch.id, zone_id=eg_zone.id, subscription_active=True)
            db.add(c_ravi)
            db.commit()

        cust_anil_usr = users["customer.anil@prasadfarm.com"]
        c_anil = db.query(Customer).filter(Customer.user_id == cust_anil_usr.id).first()
        if not c_anil:
            c_anil = Customer(id=str(uuid.uuid4()), user_id=cust_anil_usr.id, service_type=ServiceType.one_time, branch_id=vzg_branch.id, zone_id=vzg_zone.id, subscription_active=True)
            db.add(c_anil)
            db.commit()

        farm1 = db.query(Farm).filter(Farm.customer_id == c_ravi.id).first()
        if not farm1:
            farm1 = Farm(
                id=str(uuid.uuid4()), customer_id=c_ravi.id, location="Kadiyam, East Godavari",
                area=12.5, gps_lat=17.0005, gps_lng=81.7800, soil_type="Alluvial Fertile Clay",
                water_source="Borewell & Canal Drip", zone_id=eg_zone.id, notes="Mango & Coconut Intercropping Farm"
            )
            db.add(farm1)
            db.commit()

        farm2 = db.query(Farm).filter(Farm.customer_id == c_anil.id).first()
        if not farm2:
            farm2 = Farm(
                id=str(uuid.uuid4()), customer_id=c_anil.id, location="Anakapalle, Visakhapatnam",
                area=20.0, gps_lat=17.6868, gps_lng=83.0039, soil_type="Red Sandy Loam",
                water_source="Drip Irrigation System", zone_id=vzg_zone.id, notes="Dragon Fruit & Cashew Plantation"
            )
            db.add(farm2)
            db.commit()
        print("Created Customer Records & Managed Farms")

        # --- 5. LEADS ---
        leads_data = [
            {
                "type": LeadType.farm_management, "source": LeadSource.website,
                "status": LeadStatus.prospecting, "customer_id": users["customer@prasadfarm.com"].id,
                "employee_id": users["employee@prasadfarm.com"].id, "zone_id": eg_zone.id, "branch_id": rjy_branch.id,
                "farm_details": "10-acre fertile land in Kadiyam for complete organic mango management."
            },
            {
                "type": LeadType.site_management, "source": LeadSource.digital_marketing,
                "status": LeadStatus.closed_won, "customer_id": users["customer.anil@prasadfarm.com"].id,
                "employee_id": users["sita.employee@prasadfarm.com"].id, "zone_id": vzg_zone.id, "branch_id": vzg_branch.id,
                "farm_details": "20-acre dragon fruit plantation setup near Anakapalle."
            }
        ]
        for ld in leads_data:
            if not db.query(Lead).filter(Lead.customer_id == ld["customer_id"]).first():
                db.add(Lead(id=str(uuid.uuid4()), **ld))
        db.commit()

        # --- 6. PROJECTS & INVESTMENTS ---
        proj = db.query(Project).filter(Project.name == "Godavari High-Yield Organic Papaya & Teak Project").first()
        if not proj:
            proj = Project(
                id=str(uuid.uuid4()), name="Godavari High-Yield Organic Papaya & Teak Project",
                type=ProjectType.project_investment,
                description="30-acre fractional agriculture investment project with 18% projected IRR.",
                total_amount=5000000.0, funded_amount=3200000.0, status=ProjectStatus.active,
                posted_by=users["founder@prasadfarm.com"].id
            )
            db.add(proj)
            db.commit()

        if not db.query(Investment).filter(Investment.customer_id == c_anil.id).first():
            db.add(Investment(
                id=str(uuid.uuid4()), project_id=proj.id, customer_id=c_anil.id,
                type=InvestmentType.project, amount=500000.0, status=InvestmentStatus.active,
                revenue_share_percentage=18.0, expected_return=90000.0, bond_period=24
            ))
        db.commit()

        # --- 7. LAND SALES ---
        if not db.query(LandSale).filter(LandSale.customer_id == c_ravi.id).first():
            db.add(LandSale(
                id=str(uuid.uuid4()), customer_id=c_ravi.id,
                land_type=LandType.agricultural, facing="East", area=4.0,
                listed_price=8500000.0, location="Rajahmundry-Kakinada Highway",
                status=LandSaleStatus.listed, description="Prime 4-Acre Highway Facing Agriculture Land"
            ))
        db.commit()

        # --- 8. WORK ORDERS & VISITS ---
        wo = db.query(WorkOrder).filter(WorkOrder.farm_id == farm1.id).first()
        if not wo:
            wo = WorkOrder(
                id=str(uuid.uuid4()), farm_id=farm1.id, type=WorkOrderType.irrigation,
                status=WorkOrderStatus.in_progress, farm_employee_id=users["farmemployee@prasadfarm.com"].id,
                agri_officer_id=users["agriofficer@prasadfarm.com"].id, payment_status=PaymentStatus.pending,
                notes="Install Netafim drip lines and test soil NPK values."
            )
            db.add(wo)
            db.commit()

        if not db.query(Visit).filter(Visit.farm_id == farm1.id).first():
            db.add(Visit(
                id=str(uuid.uuid4()), farm_id=farm1.id, work_order_id=wo.id, farm_employee_id=users["farmemployee@prasadfarm.com"].id,
                type=VisitType.assign_visit, status=VisitStatus.completed,
                gps_lat=17.0005, gps_lng=81.7800, notes="Drip lines installed cleanly. Proof uploaded."
            ))
        db.commit()

        # --- 9. PRESCRIPTIONS & CROP DESIGNS ---
        if not db.query(Prescription).filter(Prescription.farm_id == farm1.id).first():
            db.add(Prescription(
                id=str(uuid.uuid4()), farm_id=farm1.id, agri_officer_id=users["agriofficer@prasadfarm.com"].id, work_order_id=wo.id,
                prescription_text="Minor zinc deficiency detected in young leaves. Spray Chelated Zinc 2g/L water every 15 days.",
                quote_amount=4500.0, status=PrescriptionStatus.approved
            ))
        db.commit()

        if not db.query(CropDesign).filter(CropDesign.farm_id == farm1.id).first():
            db.add(CropDesign(
                id=str(uuid.uuid4()), farm_id=farm1.id, agri_officer_id=users["agriofficer@prasadfarm.com"].id,
                best_practices="Drip fertigation + organic compost mulching.",
                land_suitability="Highly suitable for Mango & Coconut intercropping.",
                estimated_yearly_cost=120000.0, approval_status=ApprovalStatus.approved
            ))
        db.commit()

        print("\nEnterprise Data Seeding Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
