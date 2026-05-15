param(
    [string]$AgentName = "Marlowe",
    [string]$RepositoryPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Remote = "",
    [string]$Branch = "",
    [int]$PollSeconds = 60,
    [string]$LogPath = "",
    [switch]$Once
)

$ErrorActionPreference = "Stop"

if (-not $LogPath) {
    $LogPath = Join-Path $RepositoryPath ".tmp/github-pull-agent.log"
}

$logDir = Split-Path -Parent $LogPath
if ($logDir) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

function Write-AgentLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] [$AgentName] $Message" | Tee-Object -FilePath $LogPath -Append
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)

    function ConvertTo-ProcessArgument {
        param([string]$Argument)
        if ($Argument -match '[\s"]') {
            return '"' + ($Argument -replace '"', '\"') + '"'
        }
        return $Argument
    }

    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "git"
    $processInfo.WorkingDirectory = $RepositoryPath
    $processInfo.Arguments = ($Arguments | ForEach-Object { ConvertTo-ProcessArgument $_ }) -join " "
    $processInfo.UseShellExecute = $false
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true

    $process = [System.Diagnostics.Process]::Start($processInfo)
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $output = @()
    if ($stdout) {
        $output += $stdout.TrimEnd() -split "`r?`n"
    }
    if ($stderr) {
        $output += $stderr.TrimEnd() -split "`r?`n"
    }

    if ($process.ExitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $($process.ExitCode): $($output -join ' ')"
    }

    return $output
}

function Test-CleanWorktree {
    $status = Invoke-Git status --porcelain
    return -not $status
}

function Select-FirstGitLine {
    param($Value)

    if ($null -eq $Value) {
        return ""
    }

    if ($Value -is [array]) {
        if ($Value.Count -eq 0) {
            return ""
        }
        return [string]$Value[0]
    }

    return [string]$Value
}

function Get-CurrentBranch {
    $branch = Select-FirstGitLine (Invoke-Git symbolic-ref --quiet --short HEAD)
    if (-not $branch) {
        throw "repository is not on a branch; detached HEAD is not supported"
    }
    return $branch
}

function Get-WatchTarget {
    $currentBranch = Get-CurrentBranch
    $targetRemote = $Remote
    $targetBranch = $Branch

    if (-not $targetRemote) {
        try {
            $targetRemote = Select-FirstGitLine (Invoke-Git config --get "branch.$currentBranch.remote")
        }
        catch {
            $targetRemote = ""
        }
    }

    if (-not $targetBranch) {
        try {
            $mergeRef = Select-FirstGitLine (Invoke-Git config --get "branch.$currentBranch.merge")
        }
        catch {
            $mergeRef = ""
        }
        if ($mergeRef) {
            $targetBranch = $mergeRef -replace '^refs/heads/', ''
        }
    }

    $targetRemote = Select-FirstGitLine $targetRemote
    $targetBranch = Select-FirstGitLine $targetBranch

    if (-not $targetRemote -or -not $targetBranch) {
        throw "current branch '$currentBranch' does not have an upstream; set one with 'git branch --set-upstream-to <remote>/<branch>' or pass -Remote and -Branch"
    }

    return [PSCustomObject]@{
        CurrentBranch = $currentBranch
        Remote = $targetRemote
        Branch = $targetBranch
        Ref = "$targetRemote/$targetBranch"
    }
}

function Sync-IfBehind {
    $target = Get-WatchTarget
    Write-AgentLog "Checking $($target.Ref) for local branch $($target.CurrentBranch) from $RepositoryPath"

    Invoke-Git fetch --prune $target.Remote | Out-Null

    if (-not (Test-CleanWorktree)) {
        Write-AgentLog "Skipped pull: worktree has local changes."
        return
    }

    $counts = (Invoke-Git rev-list --left-right --count "HEAD...$($target.Ref)").Trim() -split "\s+"
    $ahead = [int]$counts[0]
    $behind = [int]$counts[1]

    if ($behind -eq 0) {
        Write-AgentLog "Already up to date. Local ahead=$ahead behind=$behind."
        return
    }

    if ($ahead -gt 0) {
        Write-AgentLog "Skipped pull: local branch is ahead by $ahead and behind by $behind. Manual rebase/merge needed."
        return
    }

    Write-AgentLog "Pulling $behind new commit(s) with --ff-only."
    Invoke-Git pull --ff-only $target.Remote $target.Branch | ForEach-Object {
        Write-AgentLog $_
    }
}

Write-AgentLog "GitHub pull agent started. PollSeconds=$PollSeconds Once=$Once"

do {
    try {
        Sync-IfBehind
    }
    catch {
        Write-AgentLog "Error: $($_.Exception.Message)"
    }

    if (-not $Once) {
        Start-Sleep -Seconds $PollSeconds
    }
} while (-not $Once)

Write-AgentLog "GitHub pull agent stopped."
