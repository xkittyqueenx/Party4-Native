param(
    [string]$ManifestUrl,
    [string]$GameFolder = $PSScriptRoot
)
$ErrorActionPreference = 'Stop'
$GameFolder = [IO.Path]::GetFullPath($GameFolder)
if (-not $ManifestUrl) {
    $channel = Join-Path $GameFolder 'update-channel.txt'
    if (-not (Test-Path -LiteralPath $channel)) {
        throw 'No update channel configured. Put the GitHub raw update.json URL in update-channel.txt.'
    }
    $ManifestUrl = (Get-Content -LiteralPath $channel -Raw).Trim()
}
if (-not $ManifestUrl.StartsWith('https://', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Update manifest must use HTTPS.'
}

function Safe-Target([string]$relative) {
    if ([IO.Path]::IsPathRooted($relative) -or $relative -match '(^|[/\\])\.\.([/\\]|$)' -or
        $relative -match '[:\x00-\x1f]') { throw "Unsafe update path: $relative" }
    $target = [IO.Path]::GetFullPath((Join-Path $GameFolder $relative))
    if (-not $target.StartsWith($GameFolder.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Update path leaves game folder: $relative"
    }
    return $target
}

$temp = Join-Path ([IO.Path]::GetTempPath()) ('Party4-update-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    Write-Host 'Checking for updates...'
    $manifest = Invoke-RestMethod -Uri $ManifestUrl -TimeoutSec 30
    if (-not $manifest.version -or -not $manifest.downloadUrl -or $manifest.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
        throw 'Update manifest is incomplete.'
    }
    if (-not ([string]$manifest.downloadUrl).StartsWith('https://', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Update download must use HTTPS.'
    }
    $installed = Join-Path $GameFolder 'installed-version.txt'
    if ((Test-Path -LiteralPath $installed) -and (Get-Content -LiteralPath $installed -Raw).Trim() -eq [string]$manifest.version) {
        Write-Host "Already up to date: $($manifest.version)"
        return
    }
    $zip = Join-Path $temp 'update.zip'
    Invoke-WebRequest -Uri $manifest.downloadUrl -OutFile $zip -TimeoutSec 120
    $actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
    if ($actual -ne [string]$manifest.sha256) { throw 'Downloaded update checksum does not match GitHub manifest.' }
    $expanded = Join-Path $temp 'expanded'
    Expand-Archive -LiteralPath $zip -DestinationPath $expanded
    $payload = Get-Content -LiteralPath (Join-Path $expanded 'update-payload.json') -Raw | ConvertFrom-Json
    if ([string]$payload.version -ne [string]$manifest.version) { throw 'Update version mismatch.' }
    $fileProps = @($payload.files.PSObject.Properties)
    $oldProps = $payload.previous.PSObject.Properties
    $oldMap = @{}
    foreach ($property in $oldProps) { $oldMap[$property.Name] = [string]$property.Value }
    $removals = @($payload.removed)
    foreach ($property in $fileProps) {
        $target = Safe-Target $property.Name
        $source = [IO.Path]::GetFullPath((Join-Path $expanded $property.Name))
        if (-not $source.StartsWith($expanded + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw "Invalid payload path: $($property.Name)"
        }
        if (-not (Test-Path -LiteralPath $source) -or (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne [string]$property.Value) {
            throw "Invalid update file: $($property.Name)"
        }
        if ($oldMap.ContainsKey($property.Name) -and (Test-Path -LiteralPath $target) -and
            (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $oldMap[$property.Name]) {
            throw "Installed file differs from update baseline: $($property.Name)"
        }
    }
    foreach ($relative in $removals) {
        $target = Safe-Target $relative
        if ((Test-Path -LiteralPath $target) -and $oldMap.ContainsKey($relative) -and
            (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $oldMap[$relative]) {
            throw "Installed file differs from update baseline: $relative"
        }
    }
    # The menu starts this updater and then closes the game. Give the process a
    # moment to release its DLLs before attempting any replacement.
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if (-not (Get-Process -Name 'Mario Party 4 Deluxe' -ErrorAction SilentlyContinue)) { break }
        Start-Sleep -Seconds 1
    }
    if (Get-Process -Name 'Mario Party 4 Deluxe' -ErrorAction SilentlyContinue) {
        throw 'Close Mario Party 4 Deluxe before installing the update.'
    }
    $backup = Join-Path $temp 'backup'
    New-Item -ItemType Directory -Path $backup | Out-Null
    $touched = @($fileProps | ForEach-Object Name) + $removals
    foreach ($relative in $touched) {
        $target = Safe-Target $relative
        if (Test-Path -LiteralPath $target) {
            $saved = Join-Path $backup $relative
            New-Item -ItemType Directory -Path (Split-Path $saved) -Force | Out-Null
            Copy-Item -LiteralPath $target -Destination $saved
        }
    }
    try {
        foreach ($property in $fileProps) {
            $target = Safe-Target $property.Name
            New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
            Copy-Item -LiteralPath (Join-Path $expanded $property.Name) -Destination $target -Force
        }
        foreach ($relative in $removals) {
            $target = Safe-Target $relative
            if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Force }
        }
        Set-Content -LiteralPath $installed -Value ([string]$payload.version) -NoNewline
    } catch {
        foreach ($relative in $touched) {
            $saved = Join-Path $backup $relative
            $target = Safe-Target $relative
            if (Test-Path -LiteralPath $saved) {
                Copy-Item -LiteralPath $saved -Destination $target -Force
            } elseif (Test-Path -LiteralPath $target) {
                Remove-Item -LiteralPath $target -Force
            }
        }
        throw
    }
    Write-Host "Installed $($payload.version): $($fileProps.Count) changed files, $($removals.Count) removed files."
} finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
