# migrations/versions/4312a61d695d_athlete_profile_fields_enums.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4312a61d695d"
down_revision = "91274cbc56ad"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # --- Create enum types first (idempotent with checkfirst) ---
    archery_discipline = postgresql.ENUM(
        "compound", "recurve", "barebow", "other", name="archery_discipline"
    )
    handedness = postgresql.ENUM(
        "left", "right", "ambidextrous", name="handedness"
    )
    medal = postgresql.ENUM("gold", "silver", "bronze", "none", name="medal")

    archery_discipline.create(bind, checkfirst=True)
    handedness.create(bind, checkfirst=True)
    medal.create(bind, checkfirst=True)

    # --- Athletes table: add new columns that use the enums/JSONB ---
    with op.batch_alter_table("athletes") as b:
        b.add_column(sa.Column("slug", sa.String(), nullable=True))
        b.add_column(sa.Column("hometown", sa.String(), nullable=True))
        b.add_column(
            sa.Column(
                "discipline",
                postgresql.ENUM(name="archery_discipline", create_type=False),
                nullable=True,
            )
        )
        # If you are converting an existing VARCHAR "handedness" column to enum,
        # leave it in place and convert type below. If you do NOT have that column yet
        # (fresh DB), uncomment this to add it:
        # b.add_column(
        #     sa.Column(
        #         "handedness",
        #         postgresql.ENUM(name="handedness", create_type=False),
        #         nullable=True,
        #     )
        # )

        b.add_column(sa.Column("bio_short", sa.Text(), nullable=True))
        b.add_column(sa.Column("bio_long", sa.Text(), nullable=True))
        b.add_column(sa.Column("quote_text", sa.Text(), nullable=True))
        b.add_column(sa.Column("quote_source", sa.String(), nullable=True))

        b.add_column(sa.Column("card_image_url", sa.Text(), nullable=True))
        b.add_column(sa.Column("hero_image_url", sa.Text(), nullable=True))
        b.add_column(sa.Column("video_url", sa.Text(), nullable=True))

        # JSONB with safe server_defaults so null -> [] / {}
        b.add_column(
            sa.Column(
                "gallery",
                postgresql.JSONB(),
                server_default=sa.text("'[]'::jsonb"),
                nullable=False,
            )
        )
        b.add_column(
            sa.Column(
                "socials",
                postgresql.JSONB(),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            )
        )
        b.add_column(
            sa.Column(
                "sponsors",
                postgresql.JSONB(),
                server_default=sa.text("'[]'::jsonb"),
                nullable=False,
            )
        )
        b.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    # --- OPTIONAL: convert existing VARCHAR handedness -> enum (safe if column exists) ---
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='athletes' AND column_name='handedness'
          ) THEN
            BEGIN
              -- Convert empty string to NULL first to avoid cast errors
              UPDATE athletes SET handedness=NULL WHERE handedness='';
              ALTER TABLE athletes
                ALTER COLUMN handedness TYPE handedness
                USING handedness::handedness;
            EXCEPTION WHEN undefined_column THEN
              -- column didn't exist; ignore
              NULL;
            END;
          END IF;
        END $$;
        """
    )

    # If you also create the related tables here and they reference `medal`,
    # ensure they come AFTER medal.create() above.


def downgrade():
    # Reverse the ALTER (enum -> text) if it was applied
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='athletes' AND column_name='handedness'
          )
          THEN
            BEGIN
              ALTER TABLE athletes
                ALTER COLUMN handedness TYPE TEXT
                USING handedness::text;
            EXCEPTION WHEN undefined_column THEN
              NULL;
            END;
          END IF;
        END $$;
        """
    )

    with op.batch_alter_table("athletes") as b:
        b.drop_column("updated_at")
        b.drop_column("sponsors")
        b.drop_column("socials")
        b.drop_column("gallery")
        b.drop_column("video_url")
        b.drop_column("hero_image_url")
        b.drop_column("card_image_url")
        b.drop_column("quote_source")
        b.drop_column("quote_text")
        b.drop_column("bio_long")
        b.drop_column("bio_short")
        b.drop_column("discipline")
        b.drop_column("hometown")
        b.drop_column("slug")

    bind = op.get_bind()
    # Drop enums last (only if not used by other tables)
    for enum_name in ("medal", "handedness", "archery_discipline"):
        try:
            postgresql.ENUM(name=enum_name).drop(bind, checkfirst=True)
        except Exception:
            # If still in use by another table, leave it.
            pass
