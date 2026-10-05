[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function Require([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
$testRoot = Join-Path ([IO.Path]::GetTempPath()) "snow-site-workflow-tests-$([guid]::NewGuid().ToString('N'))"
$null = New-Item -ItemType Directory -Path (Join-Path $testRoot 'scripts')
$null = New-Item -ItemType Directory -Path (Join-Path $testRoot 'theme/components/DownloadPage')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'publish-release.ps1') -Destination (Join-Path $testRoot 'scripts')
$versionFile = Join-Path $testRoot 'theme/components/DownloadPage/releaseLinks.ts'
$workflow = Join-Path $testRoot 'scripts/publish-release.ps1'
$global:SiteTestEvents = [Collections.Generic.List[string]]::new()
$global:SiteTestMode = 'success'
function global:git {
    $arguments = @($args)
    $global:LASTEXITCODE = 0
    $global:SiteTestEvents.Add($arguments[0])
    switch ($arguments[0]) {
        status { if ($global:SiteTestMode -eq 'dirty') { return ' M unrelated.ts' } }
        branch { return 'main' }
        push { if ($global:SiteTestMode -eq 'push-failure') { $global:LASTEXITCODE = 1 } }
        rev-parse { return ('a' * 40) }
        ls-remote { if ($global:SiteTestMode -eq 'remote-mismatch') { return ('b' * 40) + "`trefs/heads/main" }; return ('a' * 40) + "`trefs/heads/main" }
        add { Require ($arguments[2] -ceq 'theme/components/DownloadPage/releaseLinks.ts') 'Stage only the version source.' }
        commit { Require ($arguments[2] -ceq 'build(release): update website to 1.1.8') 'Commit the target version.' }
        default { throw "Unexpected Git operation: $($arguments[0])" }
    }
}
function global:bun {
    $global:LASTEXITCODE = 0
    $global:SiteTestEvents.Add($args[1])
    if ($args[1] -eq 'build') { throw 'Stop at verified build boundary.' }
}
function global:python {
    Require ($args[1] -ceq 'check-release-installer') 'Check the published installer before changing the website.'
    Require (($args[2..3] -join ' ') -ceq '--version 1.1.8') 'Check the target release version.'
    $global:LASTEXITCODE = if ($global:SiteTestMode -eq 'installer-failure') { 1 } else { 0 }
    $global:SiteTestEvents.Add('check-release-installer')
}
function Run-UntilBuild([string]$ExpectedError) {
    $message = ''
    try { & $workflow -Version '1.1.8' } catch { $message = $_.Exception.Message }
    Require ($message.Contains($ExpectedError)) "Expected '$ExpectedError', got '$message'."
}
try {
    [IO.File]::WriteAllText($versionFile, "export const releaseVersion = '1.1.7-beta';`n")
    $global:SiteTestMode = 'installer-failure'
    Run-UntilBuild 'python failed'
    Require ([IO.File]::ReadAllText($versionFile).Contains("releaseVersion = '1.1.7-beta'")) 'A missing or mismatched installer leaves the version source untouched.'
    Require (($global:SiteTestEvents -join ',') -ceq 'status,branch,check-release-installer') 'Failed installer validation prevents version commits, pushes, builds, and deployment.'

    $global:SiteTestEvents.Clear()
    $global:SiteTestMode = 'success'
    Run-UntilBuild 'Stop at verified build boundary'
    Require ([IO.File]::ReadAllText($versionFile).Contains("releaseVersion = '1.1.8'")) 'Update the target version.'
    Require (($global:SiteTestEvents -join ',') -ceq 'status,branch,check-release-installer,lint,add,commit,push,rev-parse,ls-remote,build') 'Verify the release installer, then commit and verify push before build.'

    $global:SiteTestEvents.Clear()
    Run-UntilBuild 'Stop at verified build boundary'
    Require (-not $global:SiteTestEvents.Contains('commit')) 'Matching versions reuse the existing commit.'

    foreach ($mode in @('push-failure', 'remote-mismatch', 'dirty')) {
        $global:SiteTestEvents.Clear()
        $global:SiteTestMode = $mode
        $errorText = switch ($mode) {
            push-failure { 'git failed' }
            remote-mismatch { 'does not match' }
            dirty { 'Commit or stash' }
        }
        Run-UntilBuild $errorText
        Require (-not $global:SiteTestEvents.Contains('build')) 'Do not build after a failed push or dirty checkout.'
    }
    $global:SiteTestEvents.Clear()
    & $workflow -Version '1.1.8' -WhatIf
    Require ($global:SiteTestEvents.Count -eq 0) 'WhatIf makes no external calls.'
    Write-Output 'Website release workflow tests passed.'
} finally {
    Remove-Item Function:\git, Function:\bun, Function:\python
    # The only recursively removed path is the verified fixture beneath the OS temp directory.
    $resolvedTestRoot = [IO.Path]::GetFullPath($testRoot)
    $separator = [IO.Path]::DirectorySeparatorChar
    $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd($separator) + $separator
    if (-not $resolvedTestRoot.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Refusing to remove a fixture outside the temporary directory.'
    }
    Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force
    Remove-Variable SiteTestEvents, SiteTestMode -Scope Global
}
