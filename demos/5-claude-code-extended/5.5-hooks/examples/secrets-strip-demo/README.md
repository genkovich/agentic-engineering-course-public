# secrets-strip-demo

Standalone демо `.claude/hooks/secrets-strip.py` — той самий sanitizer, який `debug-tool-trace.sh` і `analytics-send.sh` застосовують перед записом/відправкою.

## Запуск

```bash
cat input-dirty.json | python3 ../../.claude/hooks/secrets-strip.py
```

Або через Make з кореня демо:

```bash
make strip-demo
```

## Що замінюється на `***REDACTED***`

1. **Value-патерни в будь-якому рядку:**
   - `sk-...` (OpenAI/Anthropic-style)
   - `ghp_...`, `github_pat_...` (GitHub PAT)
   - `xox[baprs]-...` (Slack tokens)
   - `AIza...` (Google API)
   - `AKIA...` (AWS)
   - JWT (`eyJ...` 3-парт base64)
   - PEM private key blocks
2. **Sensitive ключі по імені** (case-insensitive): `password`, `secret`, `token`, `api_key`, `apikey`, `authorization`, `bearer`, `client_secret`. Значення повністю замінюється.
3. **`.env`-style рядки** виду `^[A-Z_]+=...$` — value частина замінюється.

## Очікуваний результат

Перевір `output-clean.json` поряд — приблизно так має виглядати вихід (модулюючи order ключів і indent). Жоден реальний токен не повинен пережити обробку.

## Як викликається в реальних hooks

```
debug-tool-trace.sh:
   stdin (Claude payload) → enrich → secrets-strip.py → append .claude/logs/tool-trace.jsonl

analytics-send.sh:
   stdin → secrets-strip.py → curl POST $ANALYTICS_URL
```

Якщо ти зміниш регекси у `secrets-strip.py` — обидва pipeline'и підтягнуть зміни автоматично, бо це shared helper.
