# Dockerfile - база для devcontainer і docker compose з Claude Code.
# init-firewall.sh має лежати у тій самій директорії що цей Dockerfile.

ARG TZ=Europe/Kyiv
ARG CLAUDE_CODE_VERSION=latest

FROM rust:1

ARG TZ
ARG CLAUDE_CODE_VERSION
ENV TZ=$TZ

# Базові пакети + Node.js 20 з NodeSource (потрібен для глобальної установки Claude Code через npm).
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
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Створюємо non-root користувача vscode (UID 1000) для devcontainer.
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode

# Sudoers - тільки init-firewall.sh без пароля, нічого більше.
RUN echo "vscode ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/vscode-firewall \
    && chmod 0440 /etc/sudoers.d/vscode-firewall

COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod +x /usr/local/bin/init-firewall.sh

# Глобальна установка Claude Code через npm (потрібен Node.js).
# Валідуємо CLAUDE_CODE_VERSION щоб уникнути shell injection через --build-arg.
# Дозволяємо тільки latest, semver-подібні теги, hex commits.
RUN echo "${CLAUDE_CODE_VERSION}" | grep -qE '^(latest|[0-9a-zA-Z._-]+)$' || \
    (echo "ERROR: невалідний CLAUDE_CODE_VERSION='${CLAUDE_CODE_VERSION}'" && exit 1) \
    && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"

# Підготовка Cargo директорій з правильним owner.
RUN mkdir -p /home/vscode/.cargo/registry /workspace/target \
    && chown -R vscode:vscode /home/vscode /workspace

USER vscode
WORKDIR /workspace

ENV CARGO_HOME=/home/vscode/.cargo
ENV PATH=$CARGO_HOME/bin:$PATH
