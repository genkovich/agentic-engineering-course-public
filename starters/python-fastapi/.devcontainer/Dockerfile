# Dockerfile - база для devcontainer і docker compose з Claude Code.
# init-firewall.sh має лежати у тій самій директорії що цей Dockerfile.

ARG TZ=Europe/Kyiv
ARG CLAUDE_CODE_VERSION=latest

FROM python:3.12-slim

ARG TZ
ARG CLAUDE_CODE_VERSION
ENV TZ=$TZ

# Базові системні залежності + iptables/ipset для firewall + Node для Claude Code CLI
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
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо Node.js 20 з NodeSource - потрібен щоб поставити Claude Code через npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Створюємо non-root користувача `python` (FastAPI контейнери конвенційно так роблять)
RUN groupadd --gid 1000 python \
    && useradd --uid 1000 --gid python --shell /bin/bash --create-home python

# Дозволяємо python запускати тільки init-firewall.sh через sudo без пароля
RUN echo "python ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/python-firewall \
    && chmod 0440 /etc/sudoers.d/python-firewall

COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Валідуємо CLAUDE_CODE_VERSION щоб уникнути shell injection через --build-arg.
# Дозволяємо тільки latest, semver-подібні теги, hex commits.
RUN echo "${CLAUDE_CODE_VERSION}" | grep -qE '^(latest|[0-9a-zA-Z._-]+)$' || \
    (echo "ERROR: невалідний CLAUDE_CODE_VERSION='${CLAUDE_CODE_VERSION}'" && exit 1) \
    && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"

USER python
WORKDIR /workspace
