[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)][string]$Version,
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9.-]*$')][string]$ServerHost = '120.79.232.67',
    [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$ServerUser = 'root',
    [ValidateRange(1, 65535)][int]$ServerPort = 22,
    [string]$IdentityFile,
    [string]$KnownHostsFile,
    [string]$RemoteWebRoot = '/var/www/html',
    [string]$PublicBaseUrl = 'https://snowshot.top'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($Version -notmatch '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z]+([.-][0-9A-Za-z]+)*)?$') {
    throw 'Version must be a release semantic version.'
}
if ($RemoteWebRoot -notmatch '^/[A-Za-z0-9_/-]+$' -or $RemoteWebRoot.Contains('..') -or
    $RemoteWebRoot.TrimEnd('/') -in @('', '/var', '/var/www', '/www', '/home', '/root', '/opt')) {
    throw 'RemoteWebRoot must name a dedicated existing website directory.'
}
$publicUri = [uri]$PublicBaseUrl
if ($publicUri.Scheme -ne 'https' -or $publicUri.UserInfo -or $publicUri.Query -or $publicUri.Fragment) {
    throw 'PublicBaseUrl must use HTTPS without credentials, query, or fragment.'
}
$site = Split-Path -Parent $PSScriptRoot
if (-not $PSCmdlet.ShouldProcess("$site -> ${ServerUser}@${ServerHost}:$RemoteWebRoot",
    "Commit/push Snow Shot and Mini $Version, then build and deploy website-owned files")) { return }

function Invoke-SiteTool([string]$Tool, [string[]]$Arguments) {
    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Tool failed (exit $LASTEXITCODE)." }
}
Push-Location -LiteralPath $site
try {
    $status = @(Invoke-SiteTool git @('status', '--porcelain=v1'))
    if ($status.Count) { throw 'Commit or stash website changes before running the release workflow.' }
    $branch = (Invoke-SiteTool git @('branch', '--show-current')).Trim()
    if (-not $branch) { throw 'Website checkout must be on a branch.' }
    $links = Join-Path $site 'theme/components/DownloadPage/releaseLinks.ts'
    $source = [IO.File]::ReadAllText($links)
    $pattern = "(?m)^export const releaseVersion = '[^']+';"
    if ([regex]::Matches($source, $pattern).Count -ne 1) { throw 'Expected exactly one website releaseVersion.' }
    $updated = [regex]::Replace($source, $pattern, "export const releaseVersion = '$Version';")
    if ($updated -cne $source) {
        [IO.File]::WriteAllText($links, $updated, [Text.UTF8Encoding]::new($false))
        Invoke-SiteTool bun @('run', 'lint')
        Invoke-SiteTool git @('add', '--', 'theme/components/DownloadPage/releaseLinks.ts')
        Invoke-SiteTool git @('commit', '-m', "build(release): update website to $Version")
    }
    # No build or server mutation is allowed until this push has completed successfully.
    Invoke-SiteTool git @('push', 'origin', "HEAD:refs/heads/$branch")
    $commit = (Invoke-SiteTool git @('rev-parse', 'HEAD')).Trim()
    $remote = @(Invoke-SiteTool git @('ls-remote', 'origin', "refs/heads/$branch"))
    if ($remote.Count -ne 1 -or ($remote[0] -split '\s+')[0] -cne $commit) {
        throw 'Remote website branch does not match the local commit after push.'
    }
    Invoke-SiteTool bun @('run', 'build')
    if (@(Invoke-SiteTool git @('status', '--porcelain=v1')).Count) {
        throw 'The build modified source files; commit and rerun before deploying.'
    }
    $transaction = [guid]::NewGuid().ToString('N')
    $archive = Join-Path ([IO.Path]::GetTempPath()) "snow-shot-website-$transaction.tar.gz"
    $remoteArchive = "$($RemoteWebRoot.TrimEnd('/'))/../.snow-shot-website-$transaction.tar.gz"
    $sshOptions = @('-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'UpdateHostKeys=no', '-o', 'ConnectTimeout=15')
    if ($IdentityFile) { $sshOptions += @('-i', [IO.Path]::GetFullPath($IdentityFile), '-o', 'IdentitiesOnly=yes') }
    if ($KnownHostsFile) { $sshOptions += @('-o', "UserKnownHostsFile=$([IO.Path]::GetFullPath($KnownHostsFile))") }
    $destination = "$ServerUser@$ServerHost"
    try {
        Invoke-SiteTool python @((Join-Path $PSScriptRoot 'deploy-website.py'), 'pack', '--build',
            (Join-Path $site 'doc_build'), '--archive', $archive, '--version', $Version, '--commit', $commit)
        $sha256 = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
        Invoke-SiteTool scp ($sshOptions + @('-P', "$ServerPort", $archive, "$destination`:$remoteArchive"))
        $command = "python3 - deploy --web-root $RemoteWebRoot --archive $remoteArchive --version $Version --commit $commit --sha256 $sha256"
        $info = [Diagnostics.ProcessStartInfo]::new('ssh')
        $info.UseShellExecute = $false
        $info.RedirectStandardInput = $true
        foreach ($arg in ($sshOptions + @('-p', "$ServerPort", $destination, $command))) { $info.ArgumentList.Add($arg) }
        $process = [Diagnostics.Process]::Start($info)
        try {
            $process.StandardInput.Write([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'deploy-website.py')))
            $process.StandardInput.Close()
            $process.WaitForExit()
            if ($process.ExitCode -ne 0) { throw 'Remote website deployment failed; previous website files are retained.' }
        } finally { $process.Dispose() }
        $receipt = Invoke-RestMethod -Uri "$($PublicBaseUrl.TrimEnd('/'))/website-release.json?commit=$commit" -TimeoutSec 30
        if ($receipt.version -cne $Version -or $receipt.commit -cne $commit) {
            throw 'Public website receipt does not match this deployment.'
        }
        foreach ($page in @('/', '/download.html', '/zh/', '/zh/download.html')) {
            $response = Invoke-WebRequest -Uri "$($PublicBaseUrl.TrimEnd('/'))$page" -TimeoutSec 30
            if ($response.StatusCode -ne 200) { throw "Website health check failed: $page" }
            if ($page.EndsWith('/download.html')) {
                $locale = if ($page.StartsWith('/zh/')) { 'zh' } else { 'en' }
                $response.Content | & python (Join-Path $PSScriptRoot 'deploy-website.py') check-downloads --version $Version --locale $locale
                if ($LASTEXITCODE -ne 0) { throw "Public release download verification failed: $page" }
            }
        }
        # Delete only this workflow's exact uploaded archive. Keep the previous site backup.
        Invoke-SiteTool ssh ($sshOptions + @('-p', "$ServerPort", $destination, "rm -- $remoteArchive"))
        Write-Output "Published Snow Shot and Mini website $Version ($commit) to $PublicBaseUrl."
    } finally {
        if (Test-Path -LiteralPath $archive -PathType Leaf) { Remove-Item -LiteralPath $archive }
    }
} finally { Pop-Location }
