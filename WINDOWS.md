# Курс на Windows

Матеріали курсу пишуться і записуються на macOS, тому в репо багато bash-скриптів і Makefile'ів. Це не означає, що на Windows щось недоступне — означає лише, що деякі команди запускаються інакше. Цей гайд пояснює, де що запускати, один раз — щоб не розбиратися заново у кожному уроці.

## Три середовища

На Windows у тебе є три способи запускати матеріали курсу. Вони не виключають одне одного — більшість студентів використовує перші два.

### 1. Натівний PowerShell (основний шлях)

Claude Code на Windows працює натівно — `claude`, `claude -p`, авторизація, MCP, plugins, усе без прошарків. Python теж. Тому все головне в курсі — сесії Claude Code, Python-демо, PowerShell-скрипти (`*.ps1`) — запускається просто у PowerShell:

```powershell
claude --version
python --version        # або py --version
```

Якщо при запуску `.ps1`-скрипта PowerShell скаржиться на execution policy ("running scripts is disabled"), дозволь локальні скрипти для свого користувача (один раз):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Git Bash (для `*.sh`-скриптів)

Git Bash ставиться разом із [Git for Windows](https://git-scm.com/download/win) — у більшості він уже є. У ньому запускаються bash-скрипти курсу:

```bash
bash setup-fixture.sh
```

Чого у Git Bash **немає** з коробки: `make` і `jq`. Коли скрипт уроку їх потребує, найшвидший спосіб доставити — winget у PowerShell:

```powershell
winget install jqlang.jq
winget install ezwinports.make
```

Після встановлення перезапусти термінал, щоб PATH підхопився.

### 3. WSL (повне Linux-середовище)

[WSL](https://learn.microsoft.com/en-us/windows/wsl/install) (Windows Subsystem for Linux) дає справжній Ubuntu всередині Windows: `bash`, `make`, `jq`, `apt install` — усе як на Linux. Це найнадійніший спосіб запускати **все** з репо без адаптацій, але це окреме середовище: свій домашній каталог, свій Python, окрема установка Claude Code.

Коли WSL того вартий: якщо плануєш серйозно працювати з devcontainer'ами (Module 3), CI-подібними сценаріями чи проектами, де Linux-оточення — частина задачі. Для проходження уроків вистачає PowerShell + Git Bash.

## Що де запускати

| Артефакт у репо | Де запускати на Windows |
|---|---|
| `*.py` (Python-скрипти, демо) | Натівно: `python script.py` у PowerShell |
| `*.ps1` (PowerShell-скрипти) | Натівно у PowerShell |
| `claude`, `claude -p ...` | Натівно у PowerShell |
| `*.sh` (bash-скрипти) | Git Bash (або WSL) |
| `Makefile` (`make run`, `make demo-fixture`) | WSL — або відкрий Makefile і виконай команди таргета вручну |

Останній рядок — найважливіший трюк цього гайду. Makefile — це просто список команд з іменами. Якщо `make` нема, відкрий файл, знайди свій таргет і запусти його команди руками:

```makefile
demo-fixture:
	@cd ../fixture-repo && ../sdk-cli/release-notes.sh
```

означає: перейди у `..\fixture-repo` і запусти скрипт. На Windows це буде PowerShell-еквівалент (`cd ..\fixture-repo; ..\sdk-cli\release-notes.ps1`) — у README відповідного демо такі еквіваленти виписані готовими.

## Якщо щось не запускається

1. Подивись README поруч зі скриптом — для демо з bash-залежностями там є секція Windows з готовими командами.
2. Перевір, чи це `*.sh` — тоді Git Bash, а не PowerShell.
3. Спитай Claude. Серйозно: встав у Claude Code текст помилки і шлях до скрипта — переписати bash-однострочник під PowerShell або пояснити, чого бракує в PATH, це саме та задача, яку він закриває за один хід. Ти на курсі про agentic engineering — користуйся агентом.
