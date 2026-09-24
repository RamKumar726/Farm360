"""Add database-backed one-time service catalog.

Revision ID: 20260923_services
Revises: 20260923_workflows
"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = "20260923_services"
down_revision = "20260923_workflows"
branch_labels = None
depends_on = None

_SERVICES = [
    ("Land cleaning & levelling", "Land & protection", "Clearing scrub, rocks, and levelling terrain for cultivation.", "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=600&q=80", False),
    ("Soil & water testing", "Water & soil", "Scientific lab analysis of pH, NPK, micronutrients, and water quality.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=600&q=80", False),
    ("Borewell coordination", "Water & soil", "Hydrogeological survey, drilling oversight, and pump installation.", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80", False),
    ("Drip & sprinkler installation", "Water & soil", "Automated precision irrigation systems tailored to crop geometry.", "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=600&q=80", False),
    ("Planting & orchard setup", "Gardens", "High-density fruit orchard, sapling selection, and pit preparation.", "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=600&q=80", True),
    ("Pruning & tree care", "Crop care", "Structural pruning, canopy management, and disease control.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=600&q=80", False),
    ("Nutrition & pest care", "Crop care", "Organic bio-pesticides, micronutrient drenching, and foliar spray.", "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=600&q=80", False),
    ("One-time harvest support", "Crop care", "Harvest labor management, grading, sorting, and packaging.", "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=600&q=80", True),
    ("Landscape & kitchen gardens", "Gardens", "Custom raised beds, herbs, and ornamental garden layout design.", "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=600&q=80", False),
]


def upgrade():
    op.create_table(
        "services",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False, unique=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_services_title", "services", ["title"])
    op.create_index("ix_services_category", "services", ["category"])
    op.create_index("ix_services_is_active", "services", ["is_active"])
    json_empty = "CAST('[]' AS JSON)" if op.get_bind().dialect.name == "postgresql" else "'[]'"
    insert_service = sa.text(f"""
        INSERT INTO services (id, title, category, description, image_url, features, steps,
                              is_featured, is_active, sort_order)
        VALUES (:id, :title, :category, :description, :image_url, {json_empty}, {json_empty},
                :is_featured, TRUE, :sort_order)
    """).bindparams(
        sa.bindparam("id", type_=sa.String()),
        sa.bindparam("title", type_=sa.String()),
        sa.bindparam("category", type_=sa.String()),
        sa.bindparam("description", type_=sa.Text()),
        sa.bindparam("image_url", type_=sa.String()),
        sa.bindparam("is_featured", type_=sa.Boolean()),
        sa.bindparam("sort_order", type_=sa.Integer()),
    )
    for i, (title, category, description, image, featured) in enumerate(_SERVICES):
        op.execute(insert_service.bindparams(
            id=str(uuid.uuid4()), title=title, category=category,
            description=description, image_url=image,
            is_featured=featured, sort_order=i,
        ))


def downgrade():
    op.drop_index("ix_services_is_active", table_name="services")
    op.drop_index("ix_services_category", table_name="services")
    op.drop_index("ix_services_title", table_name="services")
    op.drop_table("services")
