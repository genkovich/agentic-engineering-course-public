FROM node:24-slim

# git для робочої копії, gh для GitHub API, ca-certificates для TLS.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates \
 && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
 && apt-get update && apt-get install -y --no-install-recommends gh \
 && rm -rf /var/lib/apt/lists/*

# Закріплена версія CLI - теза відтворюваності: образ, зібраний через півроку,
# поводиться так само, як образ, зібраний сьогодні.
ARG CLAUDE_CODE_VERSION=2.1.207
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

COPY receiver.js run-issue.sh issue-worker.md /opt/duty/
RUN chmod +x /opt/duty/run-issue.sh

# Агент працює від звичайного користувача, не від root.
RUN useradd --create-home duty && chown -R duty:duty /opt/duty
USER duty
WORKDIR /home/duty

# Секретів у образі НЕМАЄ: ANTHROPIC_API_KEY, GH_TOKEN і WEBHOOK_SECRET
# приходять з env_file під час запуску.
EXPOSE 3411
CMD ["node", "/opt/duty/receiver.js"]
