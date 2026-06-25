curl -fsSL https://claude.ai/install.sh | bash
claude -p "виконай завдання з опису задачі" \
  --permission-mode acceptEdits \
  --allowedTools "Bash Read Edit Write"