& {
    param(
        [string]$RepoRoot = 'C:\dev\trader',
        [string]$VenvPython = '',
        [int]$TimeoutSeconds = 120
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $patchNumber = '280'
    $patchName = 'post_275_release_evidence_index'
    $desktop = [Environment]::GetFolderPath('Desktop')
    if ([string]::IsNullOrWhiteSpace($desktop)) { $desktop = $env:USERPROFILE }
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $reportPath = Join-Path $desktop ("patch_{0}_{1}_{2}.txt" -f $patchNumber, $patchName, $timestamp)
    $lines = New-Object System.Collections.Generic.List[string]

    function Add-Line {
        param([AllowNull()][string]$Text)
        if ($null -eq $Text) { $Text = '' }
        $lines.Add($Text) | Out-Null
    }

    function Add-Section {
        param([string]$Title)
        Add-Line ''
        Add-Line ('=' * 120)
        Add-Line $Title
        Add-Line ('=' * 120)
    }

    function Write-Report {
        $parent = Split-Path -Parent $reportPath
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($reportPath, (($lines -join [Environment]::NewLine) + [Environment]::NewLine), $utf8NoBom)
        Write-Host $reportPath
    }

    function Invoke-Captured {
        param(
            [string]$FilePath,
            [string[]]$Arguments,
            [string]$WorkingDirectory
        )
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $FilePath
        foreach ($arg in $Arguments) { [void]$psi.ArgumentList.Add($arg) }
        $psi.WorkingDirectory = $WorkingDirectory
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $psi
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        return [pscustomobject]@{
            ExitCode = [int]$process.ExitCode
            Stdout = $stdout
            Stderr = $stderr
        }
    }

    $exitCode = 1
    try {
        if ([string]::IsNullOrWhiteSpace($VenvPython)) {
            $VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
        }
        Add-Line ("Patch      : {0}" -f $patchNumber)
        Add-Line ("PatchName  : {0}" -f $patchName)
        Add-Line 'Purpose    : Validate the post-275 release evidence index.'
        Add-Line 'Safety     : Review-only/no-submit; no live behavior widening.'
        Add-Line ("RepoRoot   : {0}" -f $RepoRoot)
        Add-Line ("Python     : {0}" -f $VenvPython)
        Add-Line ("ReportPath : {0}" -f $reportPath)

        if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "Repo root not found: $RepoRoot" }
        if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Venv python not found: $VenvPython" }

        $env:PYTHONPATH = (Join-Path $RepoRoot 'src') + [System.IO.Path]::PathSeparator + $RepoRoot

        Add-Section 'DIRECT FILE EXISTENCE DOUBLE-CHECK'
        $targets = @(
            'src\trader\execution\post_275_release_evidence_index.py',
            'docs\architecture\post_275_release_evidence_index.md',
            'tests\test_post_275_release_evidence_index.py',
            'scripts\run_patch_280_post_275_release_evidence_index_tests.ps1'
        )
        foreach ($target in $targets) {
            $path = Join-Path $RepoRoot $target
            if (Test-Path -LiteralPath $path) { Add-Line ("EXISTS : {0}" -f $path) }
            else { Add-Line ("MISSING : {0}" -f $path); throw "Missing target file: $target" }
        }

        Add-Section 'COMPILE COMMAND'
        $compileArgs = @('-m', 'compileall', '-q', 'src', 'tests')
        Add-Line ("Command : {0} {1}" -f $VenvPython, ($compileArgs -join ' '))
        $compile = Invoke-Captured -FilePath $VenvPython -Arguments $compileArgs -WorkingDirectory $RepoRoot
        Add-Line ("ExitCode : {0}" -f $compile.ExitCode)
        Add-Section 'COMPILE STDOUT'
        Add-Line $compile.Stdout
        Add-Section 'COMPILE STDERR'
        Add-Line $compile.Stderr
        if ($compile.ExitCode -ne 0) { $exitCode = $compile.ExitCode; throw 'compileall failed' }

        Add-Section 'FOCUSED TEST COMMAND'
        $testArgs = @('-m', 'unittest', 'tests.test_post_275_release_evidence_index')
        Add-Line ("Command : {0} {1}" -f $VenvPython, ($testArgs -join ' '))
        $test = Invoke-Captured -FilePath $VenvPython -Arguments $testArgs -WorkingDirectory $RepoRoot
        $exitCode = $test.ExitCode
        Add-Line ("ExitCode : {0}" -f $test.ExitCode)
        Add-Section 'STDOUT'
        Add-Line $test.Stdout
        Add-Section 'STDERR'
        Add-Line $test.Stderr
    }
    catch {
        Add-Section 'EXCEPTION'
        Add-Line $_.Exception.Message
        if ($exitCode -eq 0) { $exitCode = 1 }
    }
    finally {
        Add-Section 'SUMMARY'
        Add-Line ("Patch    : {0}" -f $patchNumber)
        Add-Line ("PatchName: {0}" -f $patchName)
        Add-Line ("ExitCode : {0}" -f $exitCode)
        if ($exitCode -eq 0) { Add-Line 'Result   : PASS' } else { Add-Line 'Result   : FAIL' }
        Add-Line ("ReportPath : {0}" -f $reportPath)
        Write-Report
    }

    exit ([int]$exitCode)
}
