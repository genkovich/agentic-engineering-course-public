// Тести нормалізації: GitHub/GitLab payload → внутрішній формат HubEvent

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { normalizeGithub, normalizeGitlab } from "../src/normalize.js";

const examplesDir = join(import.meta.dirname, "..", "examples");
const loadExample = (name: string) => JSON.parse(readFileSync(join(examplesDir, name), "utf8"));

describe("normalizeGithub", () => {
  it("pull_request opened → pr_opened", () => {
    const event = normalizeGithub("pull_request", loadExample("github-pr-opened.json"));
    expect(event.source).toBe("github");
    expect(event.kind).toBe("pr_opened");
    expect(event.repo).toBe("acme/billing-api");
    expect(event.title).toContain("Add rate limiting to login endpoint");
    expect(event.url).toBe("https://github.com/acme/billing-api/pull/42");
    expect(event.acked).toBe(false);
    expect(event.id).toBeTruthy();
    expect(event.receivedAt).toBeTruthy();
  });

  it("pull_request closed + merged → pr_merged", () => {
    const payload = loadExample("github-pr-opened.json");
    payload.action = "closed";
    payload.pull_request.merged = true;
    expect(normalizeGithub("pull_request", payload).kind).toBe("pr_merged");
  });

  it("pull_request closed без merge → pr_closed", () => {
    const payload = loadExample("github-pr-opened.json");
    payload.action = "closed";
    payload.pull_request.merged = false;
    expect(normalizeGithub("pull_request", payload).kind).toBe("pr_closed");
  });

  it("pull_request synchronize → other (зберігаємо, не губимо)", () => {
    const payload = loadExample("github-pr-opened.json");
    payload.action = "synchronize";
    expect(normalizeGithub("pull_request", payload).kind).toBe("other");
  });

  it("workflow_run failure → pipeline_failed", () => {
    const event = normalizeGithub("workflow_run", loadExample("github-workflow-run-failed.json"));
    expect(event.kind).toBe("pipeline_failed");
    expect(event.title).toContain("CI");
    expect(event.title).toContain("main");
    expect(event.url).toBe("https://github.com/acme/billing-api/actions/runs/9876543210");
  });

  it("workflow_run success → pipeline_succeeded", () => {
    const payload = loadExample("github-workflow-run-failed.json");
    payload.workflow_run.conclusion = "success";
    expect(normalizeGithub("workflow_run", payload).kind).toBe("pipeline_succeeded");
  });

  it("push → push з першим рядком commit message", () => {
    const event = normalizeGithub("push", {
      ref: "refs/heads/main",
      head_commit: {
        message: "Fix typo in invoice template\n\nLonger body here",
        url: "https://github.com/acme/billing-api/commit/abc123",
      },
      repository: { full_name: "acme/billing-api", html_url: "https://github.com/acme/billing-api" },
    });
    expect(event.kind).toBe("push");
    expect(event.title).toBe("Push to refs/heads/main: Fix typo in invoice template");
    expect(event.url).toBe("https://github.com/acme/billing-api/commit/abc123");
  });

  it("невідомий тип події → other, але зберігається", () => {
    const event = normalizeGithub("deployment_status", {
      repository: { full_name: "acme/billing-api", html_url: "https://github.com/acme/billing-api" },
    });
    expect(event.kind).toBe("other");
    expect(event.title).toBe("GitHub event: deployment_status");
    expect(event.repo).toBe("acme/billing-api");
  });

  it("порожній payload не валить нормалізацію", () => {
    const event = normalizeGithub("pull_request", {});
    expect(event.kind).toBe("other");
    expect(event.repo).toBe("(unknown)");
  });
});

describe("normalizeGitlab", () => {
  it("Pipeline Hook failed → pipeline_failed", () => {
    const event = normalizeGitlab("Pipeline Hook", loadExample("gitlab-pipeline-failed.json"));
    expect(event.source).toBe("gitlab");
    expect(event.kind).toBe("pipeline_failed");
    expect(event.repo).toBe("acme/checkout-service");
    expect(event.title).toContain("Fix tax rounding for UA invoices");
    expect(event.url).toBe("https://gitlab.com/acme/checkout-service/-/pipelines/31415");
  });

  it("Pipeline Hook success → pipeline_succeeded", () => {
    const payload = loadExample("gitlab-pipeline-failed.json");
    payload.object_attributes.status = "success";
    expect(normalizeGitlab("Pipeline Hook", payload).kind).toBe("pipeline_succeeded");
  });

  it("Merge Request Hook open → pr_opened", () => {
    const event = normalizeGitlab("Merge Request Hook", {
      object_attributes: {
        action: "open",
        title: "Refactor checkout totals",
        url: "https://gitlab.com/acme/checkout-service/-/merge_requests/15",
      },
      project: {
        path_with_namespace: "acme/checkout-service",
        web_url: "https://gitlab.com/acme/checkout-service",
      },
    });
    expect(event.kind).toBe("pr_opened");
    expect(event.title).toBe("MR: Refactor checkout totals");
    expect(event.url).toBe("https://gitlab.com/acme/checkout-service/-/merge_requests/15");
  });

  it("Merge Request Hook merge → pr_merged", () => {
    const event = normalizeGitlab("Merge Request Hook", {
      object_attributes: { action: "merge", title: "x", url: "https://gitlab.com/x" },
      project: { path_with_namespace: "acme/x", web_url: "https://gitlab.com/acme/x" },
    });
    expect(event.kind).toBe("pr_merged");
  });

  it("Push Hook → push", () => {
    const event = normalizeGitlab("Push Hook", {
      ref: "refs/heads/main",
      commits: [
        { message: "older commit", url: "https://gitlab.com/acme/x/-/commit/1" },
        { message: "Add healthcheck\n\ndetails", url: "https://gitlab.com/acme/x/-/commit/2" },
      ],
      project: { path_with_namespace: "acme/x", web_url: "https://gitlab.com/acme/x" },
    });
    expect(event.kind).toBe("push");
    expect(event.title).toBe("Push to refs/heads/main: Add healthcheck");
    expect(event.url).toBe("https://gitlab.com/acme/x/-/commit/2");
  });

  it("невідомий тип події → other", () => {
    const event = normalizeGitlab("Issue Hook", {
      project: { path_with_namespace: "acme/x", web_url: "https://gitlab.com/acme/x" },
    });
    expect(event.kind).toBe("other");
    expect(event.title).toBe("GitLab event: Issue Hook");
  });
});
