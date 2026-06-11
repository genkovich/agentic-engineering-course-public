// Нормалізація webhook-подій GitHub і GitLab у внутрішній формат HubEvent.
// Ідея: MCP tools працюють з одним форматом, незалежно від того, звідки прийшла подія.

import { randomUUID } from "node:crypto";

export type HubEventSource = "github" | "gitlab";

export type HubEventKind =
  | "pr_opened"
  | "pr_merged"
  | "pr_closed"
  | "pipeline_failed"
  | "pipeline_succeeded"
  | "push"
  | "other";

export const HUB_EVENT_KINDS: HubEventKind[] = [
  "pr_opened",
  "pr_merged",
  "pr_closed",
  "pipeline_failed",
  "pipeline_succeeded",
  "push",
  "other",
];

export interface HubEvent {
  id: string;
  source: HubEventSource;
  kind: HubEventKind;
  title: string;
  repo: string;
  url: string;
  receivedAt: string;
  acked: boolean;
}

// Webhook payload приходить ззовні, тому жодних гарантій по структурі.
// Всі поля читаємо обережно, з fallback на "(unknown)".
type Payload = Record<string, any>;

function baseEvent(source: HubEventSource): HubEvent {
  return {
    id: randomUUID(),
    source,
    kind: "other",
    title: "(unknown)",
    repo: "(unknown)",
    url: "",
    receivedAt: new Date().toISOString(),
    acked: false,
  };
}

function firstLine(text: unknown): string {
  if (typeof text !== "string" || text.length === 0) return "(no message)";
  return text.split("\n")[0].trim();
}

// GitHub: тип події лежить у заголовку X-GitHub-Event,
// деталі (action, conclusion) усередині payload.
export function normalizeGithub(eventName: string, payload: Payload): HubEvent {
  const event = baseEvent("github");
  event.repo = payload?.repository?.full_name ?? "(unknown)";
  event.url = payload?.repository?.html_url ?? "";

  switch (eventName) {
    case "pull_request": {
      const action = payload?.action;
      const pr = payload?.pull_request ?? {};
      event.title = `PR: ${pr.title ?? "(no title)"}`;
      event.url = pr.html_url ?? event.url;
      if (action === "opened" || action === "reopened") {
        event.kind = "pr_opened";
      } else if (action === "closed" && pr.merged === true) {
        event.kind = "pr_merged";
      } else if (action === "closed") {
        event.kind = "pr_closed";
      } else {
        // synchronize, labeled, review_requested тощо: зберігаємо, але як "other"
        event.kind = "other";
        event.title = `PR ${action ?? "(no action)"}: ${pr.title ?? "(no title)"}`;
      }
      return event;
    }

    case "workflow_run": {
      const run = payload?.workflow_run ?? {};
      event.url = run.html_url ?? event.url;
      const name = run.name ?? "(no name)";
      const branch = run.head_branch ?? "(no branch)";
      if (run.conclusion === "failure" || run.conclusion === "timed_out" || run.conclusion === "startup_failure") {
        event.kind = "pipeline_failed";
        event.title = `CI failed: ${name} on ${branch}`;
      } else if (run.conclusion === "success") {
        event.kind = "pipeline_succeeded";
        event.title = `CI passed: ${name} on ${branch}`;
      } else {
        // requested, in_progress, cancelled тощо
        event.kind = "other";
        event.title = `CI ${run.status ?? "(no status)"}: ${name} on ${branch}`;
      }
      return event;
    }

    case "push": {
      event.kind = "push";
      const ref = payload?.ref ?? "(no ref)";
      event.title = `Push to ${ref}: ${firstLine(payload?.head_commit?.message)}`;
      event.url = payload?.head_commit?.url ?? event.url;
      return event;
    }

    default: {
      // Невідомий тип події теж зберігаємо: краще бачити у черзі, ніж мовчки губити
      event.kind = "other";
      event.title = `GitHub event: ${eventName}`;
      return event;
    }
  }
}

// GitLab: тип події у заголовку X-Gitlab-Event ("Merge Request Hook", "Pipeline Hook"...),
// деталі усередині object_attributes.
export function normalizeGitlab(eventName: string, payload: Payload): HubEvent {
  const event = baseEvent("gitlab");
  event.repo = payload?.project?.path_with_namespace ?? "(unknown)";
  event.url = payload?.project?.web_url ?? "";

  switch (eventName) {
    case "Merge Request Hook": {
      const attrs = payload?.object_attributes ?? {};
      event.title = `MR: ${attrs.title ?? "(no title)"}`;
      event.url = attrs.url ?? event.url;
      if (attrs.action === "open" || attrs.action === "reopen") {
        event.kind = "pr_opened";
      } else if (attrs.action === "merge") {
        event.kind = "pr_merged";
      } else if (attrs.action === "close") {
        event.kind = "pr_closed";
      } else {
        event.kind = "other";
        event.title = `MR ${attrs.action ?? "(no action)"}: ${attrs.title ?? "(no title)"}`;
      }
      return event;
    }

    case "Pipeline Hook": {
      const attrs = payload?.object_attributes ?? {};
      const ref = attrs.ref ?? "(no ref)";
      if (attrs.id != null && payload?.project?.web_url) {
        event.url = `${payload.project.web_url}/-/pipelines/${attrs.id}`;
      }
      if (attrs.status === "failed") {
        event.kind = "pipeline_failed";
        event.title = `Pipeline failed on ${ref}: ${firstLine(payload?.commit?.message)}`;
      } else if (attrs.status === "success") {
        event.kind = "pipeline_succeeded";
        event.title = `Pipeline passed on ${ref}: ${firstLine(payload?.commit?.message)}`;
      } else {
        // pending, running, canceled тощо
        event.kind = "other";
        event.title = `Pipeline ${attrs.status ?? "(no status)"} on ${ref}`;
      }
      return event;
    }

    case "Push Hook": {
      event.kind = "push";
      const ref = payload?.ref ?? "(no ref)";
      const commits = Array.isArray(payload?.commits) ? payload.commits : [];
      const last = commits[commits.length - 1];
      event.title = `Push to ${ref}: ${firstLine(last?.message)}`;
      event.url = last?.url ?? event.url;
      return event;
    }

    default: {
      event.kind = "other";
      event.title = `GitLab event: ${eventName}`;
      return event;
    }
  }
}
