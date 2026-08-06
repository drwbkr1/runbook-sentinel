$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = 'src'

$pythonCmd = (Get-Command python).Source
$stdoutPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0006-stdout.log'
$stderrPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0006-stderr.log'
$databasePath = Join-Path (Get-Location) 'var\live-api-baseline-0006.db'
$tracePath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0006-traces.jsonl'
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
    '--db', 'var\live-api-baseline-0006.db',
    '--trace', 'artifacts\runtime\live-api-baseline-0006-traces.jsonl',
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
    $screenshotPath = Join-Path (Get-Location) 'artifacts\verification\dashboard-baseline-0006.png'
    & $edge `
        --headless `
        --disable-gpu `
        --hide-scrollbars `
        --window-size=1440,1000 `
        --screenshot=$screenshotPath `
        http://127.0.0.1:8876/dashboard | Out-Null

    $traceText = Get-Content -Raw 'artifacts\runtime\live-api-baseline-0006-traces.jsonl'
    $verification = [pscustomobject]@{
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
        evaluation_tool_trajectory_exact = $evaluation.metrics.tool_trajectory.exact_match
        evaluation_terminal_state_exact = $evaluation.metrics.terminal_state.exact_match_rate
        evaluation_evidence_condition_coverage = $evaluation.metrics.coverage.evidence_condition_split_coverage
        evaluation_adversarial_split_coverage = $evaluation.metrics.coverage.adversarial_split_coverage
        dashboard_http_status = $dashboardResponse.StatusCode
        dashboard_csp = $dashboardResponse.Headers['Content-Security-Policy']
        dashboard_baseline_0006 = $dashboardResponse.Content.Contains('Baseline 0006')
        dashboard_terminal_metric = $dashboardResponse.Content.Contains('Terminal state exact')
        dashboard_condition_metric = $dashboardResponse.Content.Contains('Evidence condition coverage')
        dashboard_screenshot_exists = (Test-Path -LiteralPath $screenshotPath)
    }
    $checks = [ordered]@{
        health_ok = $verification.health -eq 'ok'
        checkpoint_exact = $verification.checkpoint -eq 'baseline-0006'
        outcome_exact = $verification.outcome -eq 'propose_action'
        proposal_exact = $verification.proposed_action -eq 'restart_worker'
        action_hash_bound = [bool]$verification.action_hash_bound
        execution_status_exact = $verification.execution_status -eq 'executed'
        postconditions_verified = [bool]$verification.postconditions_verified
        worker_healthy = [bool]$verification.worker_healthy
        restart_count_exact = $verification.restart_count -eq 1
        idempotent_repeat_equal = [bool]$verification.idempotent_repeat_equal
        replay_rejected = $verification.replay_http_status -eq 409
        approval_token_absent_from_trace = -not $verification.approval_token_in_trace
        evaluation_checkpoint_exact = $verification.evaluation_checkpoint -eq 'baseline-0006'
        evaluation_agent_exact = $verification.evaluation_agent -eq 'deterministic-control-v2'
        evaluation_passed = $verification.evaluation_disposition -eq 'pass'
        evaluation_tool_trajectory_exact = $verification.evaluation_tool_trajectory_exact -eq 1.0
        evaluation_terminal_state_exact = $verification.evaluation_terminal_state_exact -eq 1.0
        evaluation_evidence_condition_coverage = $verification.evaluation_evidence_condition_coverage -eq 1.0
        evaluation_adversarial_split_coverage = $verification.evaluation_adversarial_split_coverage -eq 1.0
        dashboard_http_ok = $verification.dashboard_http_status -eq 200
        dashboard_csp_present = $verification.dashboard_csp -like "*frame-ancestors 'none'*"
        dashboard_baseline_exact = [bool]$verification.dashboard_baseline_0006
        dashboard_terminal_metric_present = [bool]$verification.dashboard_terminal_metric
        dashboard_condition_metric_present = [bool]$verification.dashboard_condition_metric
        dashboard_screenshot_exists = [bool]$verification.dashboard_screenshot_exists
    }
    $receipt = [pscustomobject]@{
        status = if ($checks.Values -contains $false) { 'fail' } else { 'pass' }
        checks = $checks
        evidence = $verification
    }
    if ($receipt.status -ne 'pass') {
        throw ($receipt | ConvertTo-Json -Depth 6)
    }
    $receipt | ConvertTo-Json -Depth 6
}
finally {
    if ($serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id
        Wait-Process -Id $serverProcess.Id -ErrorAction SilentlyContinue
    }
}
