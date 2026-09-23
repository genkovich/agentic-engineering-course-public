-- Staged migration: add is_methodist flag to org_members
-- Promoted by sdlc-implement-tasks to live migrations tree with fresh timestamp.
-- data-model.md: org_members ALTER (§ "org_members (existing table — ALTER only)")

ALTER TABLE org_members
    ADD COLUMN IF NOT EXISTS is_methodist BOOLEAN NOT NULL DEFAULT false;
