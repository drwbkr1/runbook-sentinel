$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = 'src'

$pythonCmd = (Get-Command python).Source
$stdoutPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0004-stdout.log'
$stderrPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0004-stderr.log'
$databasePath = Join-Path (Get-Location) 'var\live-api-baseline-0004.db'
$tracePath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0004-traces.jsonl'
$generatedRuntimeFiles = @(
    $databasePath,
    "$databasePath-wal",
    "$databasePath-shm",
    $tracePath,
    $stdoutPath,
    $stderrPath
)
foreach ($generatedPath in $generatedRuntimeFiles) {
    if (Test-Path -LiteralPath $generatedPath) {
        Remove-Item -LiteralPath $generatedPath -Force
    }
}
$serverArgs = @(
    '-m', 'runbook_sentinel', 'serve',
    '--host', '127.0.0.1',
    '--port', '8876',
    '--db', 'var\live-api-baseline-0004.db',
    '--trace', 'artifacts\runtime\live-api-baseline-0004-traces.jsonl',
    '--evaluation', 'artifacts\evaluations\latest.json'
)

$serverProcess = Start-Process `
    -FilePath $pythonCmd `
    -ArgumentList $serverArgs `
    -WorkingDirectory (Get-Location) `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

try {
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8876/health' -TimeoutSec 2
            $ready = $true
            break
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }
    if (-not $ready) {
        throw 'API did not become ready'
    }

    $run = Invoke-RestMethod `
        -Method Post `
        -Uri 'http://127.0.0.1:8876/api/runs' `
        -ContentType 'application/json' `
        -Body (@{scenario_id = 'dev-worker-backlog'} | ConvertTo-Json -Compress)

    $approval = Invoke-RestMethod `
        -Method Post `
        -Uri ("http://127.0.0.1:8876/api/proposals/{0}/approve" -f $run.proposal.id) `
        -ContentType 'application/json' `
        -Body (@{actor = 'verified-local-operator'; ttl_seconds = 300} | ConvertTo-Json -Compress)

    $idempotencyKey = "live-api-{0}" -f ([guid]::NewGuid().ToString('N'))
    $executionBody = @{
        approval_token = $approval.approval_token
        idempotency_key = $idempotencyKey
    } | ConvertTo-Json -Compress
    $executionUri = "http://127.0.0.1:8876/api/proposals/{0}/execute" -f $run.proposal.id
    $execution = Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $executionBody
    $cached = Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $executionBody

    $replayStatus = 0
    try {
        $replayBody = @{
            approval_token = $approval.approval_token
            idempotency_key = "$idempotencyKey-replay"
        } | ConvertTo-Json -Compress
        Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $replayBody | Out-Null
    }
    catch {
        $replayStatus = [int]$_.Exception.Response.StatusCode
    }

    $incident = Invoke-RestMethod -Uri ("http://127.0.0.1:8876/api/incidents/{0}" -f $run.incident_id)
    $evaluation = Invoke-RestMethod -Uri 'http://127.0.0.1:8876/api/evaluation'
    $dashboardResponse = Invoke-WebRequest -Uri 'http://127.0.0.1:8876/dashboard' -UseBasicParsing

    $edgeCandidates = @(
        'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    )
    $edge = $edgeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $edge) {
        throw 'Microsoft Edge executable not found'
    }
    $screenshotPath = Join-Path (Get-Location) 'artifacts\verification\dashboard-baseline-0004.png'
    & $edge `
        --headless `
        --disable-gpu `
        --hide-scrollbars `
        --window-size=1440,1000 `
        --screenshot=$screenshotPath `
        http://127.0.0.1:8876/dashboard | Out-Null

    $traceText = Get-Content -Raw 'artifacts\runtime\live-api-baseline-0004-traces.jsonl'
    [pscustomobject]@{
        health = $health.status
        checkpoint = $health.checkpoint
        outcome = $run.outcome
        proposed_action = $run.proposal.action
        decision_context_configuration = $run.decision_context_configuration
        full_retrieval_count = $run.retrieved_document_ids.Count
        decision_document_count = $run.decision_document_ids.Count
        action_hash_bound = ($approval.action_hash -eq $run.proposal.action_hash)
        execution_status = $execution.status
        postconditions_verified = $execution.postconditions_verified
        worker_healthy = $incident.state.worker_healthy
        restart_count = $incident.state.restart_count
        idempotent_repeat_equal = (($cached | ConvertTo-Json -Compress) -eq ($execution | ConvertTo-Json -Compress))
        replay_http_status = $replayStatus
        approval_token_in_trace = $traceText.Contains($approval.approval_token)
        evaluation_checkpoint = $evaluation.checkpoint
        evaluation_agent = $evaluation.agent_configuration
        evaluation_disposition = $evaluation.gates.baseline_disposition
        dashboard_http_status = $dashboardResponse.StatusCode
        dashboard_csp = $dashboardResponse.Headers['Content-Security-Policy']
        dashboard_screenshot_exists = (Test-Path -LiteralPath $screenshotPath)
    } | ConvertTo-Json -Depth 5
}
finally {
    if ($serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id
        Wait-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue
    }
}
