# release-notes.ps1 — let Claude Agent SDK generate release notes from git
# history. PowerShell port of release-notes.sh for Windows students.
#
# Works in Windows PowerShell 5.1+ and PowerShell 7 (pwsh) on any OS.
#
# Usage:
#   cd ..\fixture-repo
#   ..\sdk-cli\release-notes.ps1
#
# Requirements:
#   - cwd is a git repository with at least one release tag and a
#     `docs/CHANGELOG.md` that follows Keep a Changelog conventions
#   - claude CLI in PATH
#   - Authenticated to Claude: either an active OAuth session
#     (`claude auth login`, recommended for local dev with Max/Pro/Team
#     subscription) or `ANTHROPIC_API_KEY` env var (CI/CD)
#
# What it demonstrates — same as release-notes.sh:
#   - `claude -p` running headlessly with a real agent loop (3-5 turns:
#     Read CHANGELOG → Bash git log → Read README → Edit CHANGELOG → Read)
#   - Tight `--allowed-tools` prefix matching across three dimensions:
#     a Bash prefix, a Read directory glob, and an Edit directory glob
#   - `--max-turns` as a production budget guard
#   - `--output-format json` + `--json-schema` so the structured release
#     notes are validated against a schema, not parsed from prose
#   - `--model claude-haiku-4-5` — release notes is a structured rewriting
#     task; Haiku handles it for cents on the dollar versus Sonnet/Opus
#
# Trust model
#   Agent edits `docs/CHANGELOG.md` in the working tree as a *suggestion*.
#   The script does NOT commit or push. After the run, inspect `git diff`
#   and choose:
#     - `git restore docs/CHANGELOG.md`   — reject the suggestion
#     - `git add -p; git commit`          — accept it
#     - export the diff as a patch and apply it elsewhere

$ErrorActionPreference = 'Stop'

$IsWindowsHost = $env:OS -eq 'Windows_NT'

# Windows PowerShell 5.1 defaults to ASCII/codepage encodings around native
# commands. Force UTF-8 both ways so the prompt's unicode survives the pipe
# and Claude's JSON output decodes correctly.
$OutputEncoding = [System.Text.Encoding]::UTF8
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# Native-command argument passing differs between PowerShell editions. Pin
# the behavior to 'Legacy' where the preference exists (pwsh 7.2+) so the
# manual quote-escaping below works identically on 5.1 and 7.x on Windows.
if ($IsWindowsHost -and (Get-Variable PSNativeCommandArgumentPassing -ErrorAction SilentlyContinue)) {
    $PSNativeCommandArgumentPassing = 'Legacy'
}

function ConvertTo-NativeArg([string]$Value) {
    # On Windows the command line is re-parsed by the native app's runtime;
    # embedded double quotes must be backslash-escaped or they get eaten.
    # On macOS/Linux args reach the process verbatim — no escaping needed.
    if ($IsWindowsHost) { return ($Value -replace '"', '\"') }
    return $Value
}

function Write-Stderr([string]$Message) {
    [Console]::Error.WriteLine($Message)
}

$PromptFile = Join-Path $PSScriptRoot 'prompts/generate-release-notes.md'

# ──────────────────────────────────────────────────────────────────
# Pre-flight — same checks as release-notes.sh
# ──────────────────────────────────────────────────────────────────

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Stderr 'ERROR: claude CLI not found in PATH.'
    Write-Stderr '       See https://docs.claude.com for installation.'
    exit 1
}

# Accept either OAuth session (claude auth login) or env var (CI/CD).
# Order matters: in CI the env var is always present, so we check it first
# and avoid invoking `claude auth status` (which may fail without OAuth).
if ($env:ANTHROPIC_API_KEY) {
    # env var present — OK
}
elseif ((claude auth status --json 2>$null | Out-String) -match '"loggedIn":\s*true') {
    # OAuth session active — OK
}
else {
    Write-Stderr 'ERROR: not authenticated to Claude.'
    Write-Stderr '       Choose one:'
    Write-Stderr "         - Run 'claude auth login' (OAuth, recommended for local dev)"
    Write-Stderr '         - Or set ANTHROPIC_API_KEY (CI/CD, GitHub Secrets)'
    exit 1
}

if (-not (Test-Path $PromptFile)) {
    Write-Stderr "ERROR: prompt file missing: $PromptFile"
    exit 1
}

if (-not (Test-Path '.git')) {
    Write-Stderr 'ERROR: cwd is not a git repository.'
    Write-Stderr '       Expected to be invoked from inside fixture-repo/.'
    exit 1
}

if (-not (Test-Path 'docs/CHANGELOG.md')) {
    Write-Stderr 'ERROR: docs/CHANGELOG.md not found.'
    Write-Stderr '       Run setup_fixture.py first.'
    exit 1
}

if (-not ((git tag -l | Out-String).Trim())) {
    Write-Stderr 'ERROR: no git tags in cwd — release notes need a previous release to diff against.'
    exit 1
}

$Prompt = Get-Content -Raw -Encoding UTF8 $PromptFile

# ──────────────────────────────────────────────────────────────────
# JSON schema — validated against Claude's final response
# ──────────────────────────────────────────────────────────────────
#
# This is the same schema used by release-notes.sh and
# sdk-python/generate_release_notes.py. Keep them in sync.

$Schema = @'
{
  "type": "object",
  "properties": {
    "version":      {"type": "string"},
    "release_date": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string", "enum": ["Added", "Changed", "Fixed", "Removed"]},
          "items": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "items"]
      }
    }
  },
  "required": ["version", "release_date", "sections"]
}
'@

# Compact to a single line without spaces: a space-free argument never gets
# re-quoted by PowerShell, which sidesteps most Windows quoting traps.
$SchemaArg = ConvertTo-NativeArg ($Schema | ConvertFrom-Json | ConvertTo-Json -Depth 10 -Compress)

# ──────────────────────────────────────────────────────────────────
# Invoke Claude — real agent loop with three-dimensional permissions
# ──────────────────────────────────────────────────────────────────
#
# Permissions cheat-sheet (this is exactly Slide 8 in the lecture):
#   - Bash(git log *) — agent can run any `git log` invocation (and only
#                      that — `git tag`, `git push`, `rm` are blocked)
#   - Read(docs/**)  — agent can read everything under docs/ (CHANGELOG,
#                      README) but not src/, tests/, or root files
#   - Edit(docs/**)  — agent can only edit files under docs/, never src/
# Anything else (rm, git commit, curl, Write outside docs/, ...) is blocked.
#
# --max-turns 6 is the production guardrail from Slide 13: enough for the
# 3-5 turn loop with one turn of headroom.
#
# The prompt is piped via stdin instead of being passed as an argument:
# multi-line markdown with quotes and angle brackets does not survive the
# Windows command-line re-parsing reliably, stdin always does.

$RawResponse = $Prompt | & claude -p `
    --allowed-tools 'Bash(git log *)' 'Read(docs/**)' 'Edit(docs/**)' `
    --model claude-haiku-4-5 `
    --output-format json `
    --json-schema $SchemaArg `
    --max-turns 6
$ClaudeExit = $LASTEXITCODE
$ResponseText = (@($RawResponse) -join "`n").Trim()

if ($ClaudeExit -ne 0) {
    Write-Stderr "[claude] exited with code $ClaudeExit — raw response below"
    Write-Stderr $ResponseText
    exit $ClaudeExit
}

# ──────────────────────────────────────────────────────────────────
# Normalize response shape across claude CLI versions
# ──────────────────────────────────────────────────────────────────
#
# Older claude (< 2.x): --output-format json returns a single object with
# `.result`, `.total_cost_usd`, `.is_error`, etc. at the top level.
# Newer claude (2.x+): same flag returns a JSON array of messages; the
# final element has `type: "result"` and carries those same fields.
# Pull the result-typed payload regardless of which shape we got.

try {
    $Parsed = ConvertFrom-Json -InputObject $ResponseText
}
catch {
    Write-Stderr '[claude] response is not valid JSON — raw response below'
    Write-Stderr $ResponseText
    exit 1
}

$Items = @($Parsed)
$ResultObj = $Items |
    Where-Object { $_.PSObject.Properties['type'] -and $_.type -eq 'result' } |
    Select-Object -Last 1
if ($null -eq $ResultObj) { $ResultObj = $Items[0] }

function Get-Field($Object, [string]$Name, $Default) {
    if ($null -ne $Object -and $Object.PSObject.Properties[$Name] -and $null -ne $Object.$Name) {
        return $Object.$Name
    }
    return $Default
}

# ──────────────────────────────────────────────────────────────────
# Summary on stderr — cost, duration, turns, error status
# ──────────────────────────────────────────────────────────────────

$Cost     = Get-Field $ResultObj 'total_cost_usd' 'n/a'
$Duration = Get-Field $ResultObj 'duration_ms'    'n/a'
$Turns    = Get-Field $ResultObj 'num_turns'      'n/a'
$IsError  = Get-Field $ResultObj 'is_error'       $false

Write-Stderr "[claude] cost=`$$Cost duration=${Duration}ms turns=$Turns is_error=$IsError"

if ($IsError -eq $true) {
    Write-Stderr '[claude] agent reported an error — raw response below'
    Write-Stderr $ResponseText
    exit 1
}

# ──────────────────────────────────────────────────────────────────
# Schema-validated JSON payload → stdout
# ──────────────────────────────────────────────────────────────────
#
# Where the structured output lives depends on CLI version:
#   - claude 2.x+: `.structured_output` is a native JSON object built from
#     the response and validated against --json-schema.
#   - claude < 2.x: `.result` is a JSON string (also validated).
# Fall back to raw `.result` if neither shape parses — at least the viewer
# still sees what the agent said.

$Payload = Get-Field $ResultObj 'structured_output' $null
if ($null -eq $Payload) {
    $RawResult = Get-Field $ResultObj 'result' $null
    if ($RawResult -is [string]) {
        try { $Payload = ConvertFrom-Json -InputObject $RawResult }
        catch { $Payload = $RawResult }
    }
    else {
        $Payload = $RawResult
    }
}

if ($Payload -is [string]) {
    Write-Output $Payload
}
else {
    $Payload | ConvertTo-Json -Depth 10
}

# ──────────────────────────────────────────────────────────────────
# Trust-but-verify: show the actual git diff so the viewer sees exactly
# what the agent changed (separate from the JSON the agent returned).
# ──────────────────────────────────────────────────────────────────

Write-Stderr ''
Write-Stderr '--- actual git diff (what agent edited in the working tree) ---'
git diff -- docs/CHANGELOG.md 2>&1 | ForEach-Object { Write-Stderr "$_" }
Write-Stderr '--- end git diff ---'
Write-Stderr ''
Write-Stderr '[hint] inspect the diff above. To accept: git add -p; git commit.'
Write-Stderr '[hint] To reject:                  git restore docs/CHANGELOG.md'
Write-Stderr '[hint] To port elsewhere:          git diff -- docs/CHANGELOG.md > release.patch; git apply release.patch'
