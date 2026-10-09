#!/usr/bin/env node
import fs from "node:fs";

const file = process.argv[2];
if (!file) {
  console.error("Usage: validate-verdict.mjs /path/to/verdict.json");
  process.exit(2);
}

let value;
try {
  value = JSON.parse(fs.readFileSync(file, "utf8"));
} catch (error) {
  console.error(`Invalid JSON: ${error.message}`);
  process.exit(1);
}

const keys = [
  "schema_version",
  "status",
  "should_open_issue",
  "summary",
  "evidence",
  "recommended_action",
  "dedupe_key",
];
const sameKeys =
  Object.keys(value).sort().join("\n") === [...keys].sort().join("\n");
const valid =
  value &&
  typeof value === "object" &&
  !Array.isArray(value) &&
  sameKeys &&
  value.schema_version === 1 &&
  ["healthy", "anomaly"].includes(value.status) &&
  typeof value.should_open_issue === "boolean" &&
  typeof value.summary === "string" &&
  value.summary.length >= 1 &&
  value.summary.length <= 500 &&
  Array.isArray(value.evidence) &&
  value.evidence.length >= 1 &&
  value.evidence.length <= 8 &&
  value.evidence.every(
    (item) => typeof item === "string" && item.length >= 1 && item.length <= 300
  ) &&
  ["none", "investigate", "rollback"].includes(value.recommended_action) &&
  typeof value.dedupe_key === "string" &&
  /^release-[A-Za-z0-9._-]+$/.test(value.dedupe_key);

if (!valid) {
  console.error("Verdict does not match the required schema");
  process.exit(1);
}

console.log("PASS: verdict schema is valid");
