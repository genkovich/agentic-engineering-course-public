# Dockerfile - база для devcontainer і docker compose з Claude Code.
# init-firewall.sh має лежати у тій самій директорії що цей Dockerfile.

ARG TZ=Europe/Kyiv
ARG CLAUDE_CODE_VERSION=latest

FROM node:20

ARG TZ
ARG CLAUDE_CODE_VERSION
ENV TZ=$TZ

RUN apt-get update && apt-get install -y --no-install-recommends \
    iptables \
    ipset \
    sudo \
    curl \
    git \
    zsh \
    fzf \
    vim \
    less \
    python3 \
    ca-certificates \
    bubblewrap \
    socat \
    && rm -rf /var/lib/apt/lists/*

RUN printf '%s\n' \
      "node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" \
      "node ALL=(root) NOPASSWD: /usr/sbin/iptables -L*, /usr/sbin/ip6tables -L*" \
      > /etc/sudoers.d/node-firewall \
    && chmod 0440 /etc/sudoers.d/node-firewall

COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Валідуємо CLAUDE_CODE_VERSION щоб уникнути shell injection через --build-arg.
# Дозволяємо тільки latest, semver-подібні теги, hex commits.
RUN echo "${CLAUDE_CODE_VERSION}" | grep -qE '^(latest|[0-9a-zA-Z._-]+)$' || \
    (echo "ERROR: невалідний CLAUDE_CODE_VERSION='${CLAUDE_CODE_VERSION}'" && exit 1) \
    && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"

# Готуємо каталоги під named volume-и, щоб non-root node мав права на запис
# (свіжий named volume успадковує ownership із mount-point образу).
RUN mkdir -p /home/node/.claude /commandhistory \
    && chown -R node:node /home/node/.claude /commandhistory

USER node
WORKDIR /workspace
