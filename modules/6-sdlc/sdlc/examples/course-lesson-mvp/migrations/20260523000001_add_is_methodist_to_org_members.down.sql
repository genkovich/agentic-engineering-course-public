-- Rollback: remove is_methodist flag from org_members

ALTER TABLE org_members
    DROP COLUMN IF EXISTS is_methodist;
