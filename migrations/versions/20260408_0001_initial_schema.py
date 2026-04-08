"""initial schema"""

from alembic import op
import sqlalchemy as sa

revision = "20260408_0001"
down_revision = None
branch_labels = None
depends_on = None

team_status = sa.Enum("pending", "active", "disabled", name="team_status")


def upgrade() -> None:
    bind = op.get_bind()
    team_status.create(bind, checkfirst=True)

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_name", sa.String(length=120), nullable=False),
        sa.Column("captain_name", sa.String(length=120), nullable=False),
        sa.Column("captain_email", sa.String(length=255), nullable=False),
        sa.Column("captain_phone", sa.String(length=30), nullable=True),
        sa.Column("captain_line_user_id", sa.String(length=120), nullable=True),
        sa.Column("status", team_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("team_name"),
        sa.UniqueConstraint("captain_email"),
    )
    op.create_index("ix_teams_id", "teams", ["id"], unique=False)

    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("is_alumni", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_members_id", "members", ["id"], unique=False)

    op.create_table(
        "email_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_email_verifications_id", "email_verifications", ["id"], unique=False)
    op.create_index(
        "ix_email_verifications_token_hash",
        "email_verifications",
        ["token_hash"],
        unique=False,
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("line_user_id", sa.String(length=120), nullable=False),
        sa.Column("session_token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("session_token_hash"),
    )
    op.create_index("ix_sessions_id", "sessions", ["id"], unique=False)

    op.create_table(
        "blacklists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_blacklists_id", "blacklists", ["id"], unique=False)
    op.create_index("ix_blacklists_value", "blacklists", ["value"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_type", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_blacklists_value", table_name="blacklists")
    op.drop_index("ix_blacklists_id", table_name="blacklists")
    op.drop_table("blacklists")

    op.drop_index("ix_sessions_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_email_verifications_token_hash", table_name="email_verifications")
    op.drop_index("ix_email_verifications_id", table_name="email_verifications")
    op.drop_table("email_verifications")

    op.drop_index("ix_members_id", table_name="members")
    op.drop_table("members")

    op.drop_index("ix_teams_id", table_name="teams")
    op.drop_table("teams")

    bind = op.get_bind()
    team_status.drop(bind, checkfirst=True)
