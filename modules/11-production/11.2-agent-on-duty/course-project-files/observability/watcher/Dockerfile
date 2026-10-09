FROM node:24.17.0-bookworm-slim

ARG CLAUDE_CODE_VERSION=2.1.207
RUN npm install --global "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
  && npm cache clean --force

WORKDIR /watcher/runtime
RUN mkdir -p artifacts .claude/skills/review-release-health \
  && chown -R node:node /watcher

COPY --chown=node:node observability/watcher/server.mjs ./server.mjs
COPY --chown=node:node .claude/skills/review-release-health \
  ./.claude/skills/review-release-health

USER node
EXPOSE 3001
CMD ["node", "server.mjs"]
