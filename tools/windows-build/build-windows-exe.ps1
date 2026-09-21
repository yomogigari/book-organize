param(
    [string]$RepoRoot = "",
    [string]$OutputRoot = "",
    [ValidateSet("standalone", "onefile")]
    [string]$Mode = "standalone",
    [switch]$CleanOutput,
    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Builder = Join-Path $ScriptDir 'build-windows-exe.py'

$BuilderArgs = @(
    $Builder,
    '--mode',
    $Mode
)

if ($RepoRoot -ne "") {
    $BuilderArgs += @('--repo-root', $RepoRoot)
}
if ($OutputRoot -ne "") {
    $BuilderArgs += @('--output-root', $OutputRoot)
}
if ($CleanOutput) {
    $BuilderArgs += '--clean-output'
}
if ($AllowDirty) {
    $BuilderArgs += '--allow-dirty'
}

& uv run --no-project --python 3.12 @BuilderArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
