"""initial_schema

Revision ID: 7115672e37d8
Revises: 
Create Date: 2026-10-21 09:46:22.167992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7115672e37d8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('doctors',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('specialization', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doctors_email'), 'doctors', ['email'], unique=True)
    op.create_table('patients',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_email'), 'patients', ['email'], unique=True)
    op.create_table('appointments',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('doctor_id', sa.String(length=36), nullable=False),
    sa.Column('patient_id', sa.String(length=36), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('cancellation_reason', sa.Text(), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_doctor_id'), 'appointments', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_appointments_end_time'), 'appointments', ['end_time'], unique=False)
    op.create_index(op.f('ix_appointments_patient_id'), 'appointments', ['patient_id'], unique=False)
    op.create_index(op.f('ix_appointments_start_time'), 'appointments', ['start_time'], unique=False)
    op.create_index(op.f('ix_appointments_status'), 'appointments', ['status'], unique=False)
    op.create_index('uq_doctor_active_slot', 'appointments', ['doctor_id', 'start_time'], unique=True, postgresql_where=sa.text("status != 'CANCELLED'"), sqlite_where=sa.text("status != 'CANCELLED'"))
    op.create_table('doctor_working_hours',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('doctor_id', sa.String(length=36), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=False, comment='0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday'),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('doctor_id', 'day_of_week', name='uq_doctor_day_of_week')
    )
    op.create_index(op.f('ix_doctor_working_hours_doctor_id'), 'doctor_working_hours', ['doctor_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_doctor_working_hours_doctor_id'), table_name='doctor_working_hours')
    op.drop_table('doctor_working_hours')
    op.drop_index('uq_doctor_active_slot', table_name='appointments', postgresql_where=sa.text("status != 'CANCELLED'"), sqlite_where=sa.text("status != 'CANCELLED'"))
    op.drop_index(op.f('ix_appointments_status'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_start_time'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_patient_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_end_time'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_doctor_id'), table_name='appointments')
    op.drop_table('appointments')
    op.drop_index(op.f('ix_patients_email'), table_name='patients')
    op.drop_table('patients')
    op.drop_index(op.f('ix_doctors_email'), table_name='doctors')
    op.drop_table('doctors')
