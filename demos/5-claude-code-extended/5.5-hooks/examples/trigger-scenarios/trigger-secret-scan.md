# Trigger: secrets-scan (recipe-3)

## Промпт для Claude (копі-паст)

> Створи файл `unsafe.js` з простим Express-handler:
>
> ```js
> app.post("/exec", (req, res) => {
>   const result = eval(req.body.code);
>   res.send(result);
> });
> ```

## Що має статись

1. Claude викличе `Write` на `unsafe.js` з відповідним content.
2. PreToolUse matcher `Edit|Write|MultiEdit` спрацює — викличеться `recipe-3-secrets-scan.py`.
3. Python скрипт прогонить content через паттерни і знайде `eval(`.
4. У stderr полетить:
   ```
   SECURITY WARNING (recipe-3-secrets-scan):
     · eval() — code injection risk: matched /\beval\s*\(/

   Review the diff and either rewrite the unsafe construct or move secrets...
   ```
5. exit 2 → Write не відбудеться, Claude отримає warning.

## Варіації для скринкасту

- Спробуй `innerHTML = req.body.html` — теж заблокується.
- Додай у файл `const KEY = "REDACTED_OPENAI_KEY_PLACEHOLDER"` — використай OpenAI key format у скринкасті, тут placeholder щоб не тригерити push protection — спрацює patterns на API key.
- Створи `.github/workflows/ci.yml` з `run: echo "${{ github.event.pull_request.title }}"` — GHA injection guard.

## На чому акцентувати

- **3 тип hook — Python script**, slide 3 (command + interpreter, не bash).
- Той самий `recipe-3-secrets-scan.py` — це по суті анропіківський `security-guidance` плагін у мініатюрі (slide 6.3).
- Власні правила додаються як ще один tuple у `PATTERNS`.
