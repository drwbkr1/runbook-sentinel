$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = if ($env:RUNBOOK_SENTINEL_PYTHONPATH) { $env:RUNBOOK_SENTINEL_PYTHONPATH } else { 'src' }

$pythonCmd = (Get-Command python).Source
$stdoutPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0012-stdout.log'
$stderrPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0012-stderr.log'
$databasePath = Join-Path (Get-Location) 'var\live-api-baseline-0012.db'
$tracePath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0012-traces.jsonl'
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
    '--port', '8877',
    '--db', 'var\live-api-baseline-0012.db',
    '--trace', 'artifacts\runtime\live-api-baseline-0012-traces.jsonl',
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
            $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8877/health' -TimeoutSec 2
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
        -Uri 'http://127.0.0.1:8877/api/runs' `
        -ContentType 'application/json' `
        -Body (@{scenario_id = 'dev-worker-backlog-stale-evidence-flood'} | ConvertTo-Json -Compress)

    $approval = Invoke-RestMethod `
        -Method Post `
        -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $run.proposal.id) `
        -ContentType 'application/json' `
        -Body (@{actor = 'verified-local-operator'; ttl_seconds = 300} | ConvertTo-Json -Compress)

    $idempotencyKey = "live-api-{0}" -f ([guid]::NewGuid().ToString('N'))
    $executionBody = @{
        approval_token = $approval.approval_token
        idempotency_key = $idempotencyKey
    } | ConvertTo-Json -Compress
    $executionUri = "http://127.0.0.1:8877/api/proposals/{0}/execute" -f $run.proposal.id
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

    $incident = Invoke-RestMethod -Uri ("http://127.0.0.1:8877/api/incidents/{0}" -f $run.incident_id)
    $evaluation = Invoke-RestMethod -Uri 'http://127.0.0.1:8877/api/evaluation'
    $dashboardResponse = Invoke-WebRequest -Uri 'http://127.0.0.1:8877/dashboard' -UseBasicParsing

    $edgeCandidates = @(
        'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    )
    $edge = $edgeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $edge) {
        throw 'Microsoft Edge executable not found'
    }
    $screenshotPath = Join-Path (Get-Location) 'artifacts\verification\dashboard-baseline-0012.png'
    & $edge `
        --headless `
        --disable-gpu `
        --hide-scrollbars `
        --window-size=1440,1000 `
        --screenshot=$screenshotPath `
        http://127.0.0.1:8877/dashboard | Out-Null

    $traceText = Get-Content -Raw 'artifacts\runtime\live-api-baseline-0012-traces.jsonl'
    $staleMetadataExact = $run.decision_stale_document_ids.Count -eq 3
    foreach ($staleId in $run.decision_stale_document_ids) {
        $fields = @($run.decision_document_fields.PSObject.Properties[$staleId].Value)
        if (($fields -join ',') -ne 'id,kind,observed_at') {
            $staleMetadataExact = $false
        }
    }
    $verification = [pscustomobject]@{
        health = $health.status
        checkpoint = $health.checkpoint
        outcome = $run.outcome
        proposed_action = $run.proposal.action
        decision_context_configuration = $run.decision_context_configuration
        retrieval_configuration = $run.retriever
        full_retrieval_count = $run.retrieved_document_ids.Count
        decision_document_count = $run.decision_document_ids.Count
        fresh_document_first = $run.retrieved_document_ids[0] -eq 'telemetry-worker-current'
        fresh_decision_evidence_retained = $run.decision_document_ids -contains 'telemetry-worker-current'
        stale_metadata_exact = $staleMetadataExact
        stale_payload_characters = $run.decision_stale_payload_characters
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
        evaluation_behavioral_relation_exact = $evaluation.metrics.behavioral_relations.exact_match_rate
        evaluation_retrieval_configuration = $evaluation.retrieval_configuration
        evaluation_stress_evidence_recall = $evaluation.metrics.retrieval_stress.expected_project_evidence_recall_at_4
        evaluation_stress_decision_retention = $evaluation.metrics.retrieval_stress.decision_evidence_retention_rate
        evaluation_stress_exact_behavior = $evaluation.metrics.retrieval_stress.exact_behavior_retention_rate
        evaluation_fresh_evidence_recall = $evaluation.metrics.stale_evidence_stress.fresh_project_evidence_recall_at_4
        evaluation_fresh_decision_retention = $evaluation.metrics.stale_evidence_stress.fresh_decision_evidence_retention_rate
        evaluation_stale_stress_exact_behavior = $evaluation.metrics.stale_evidence_stress.exact_behavior_retention_rate
        evaluation_stale_identity_retention = $evaluation.metrics.stale_payload_projection.stale_identity_retention_rate
        evaluation_stale_metadata_projection = $evaluation.metrics.stale_payload_projection.stale_metadata_projection_rate
        evaluation_stale_payload_exposure = $evaluation.metrics.stale_payload_projection.stale_payload_exposure_rate
        evaluation_fresh_payload_retention = $evaluation.metrics.stale_payload_projection.fresh_payload_retention_rate
        dashboard_http_status = $dashboardResponse.StatusCode
        dashboard_csp = $dashboardResponse.Headers['Content-Security-Policy']
        dashboard_baseline_0012 = $dashboardResponse.Content.Contains('Baseline 0012')
        dashboard_stale_baseline_absent = -not ($dashboardResponse.Content.Contains('Baseline 0010') -or $dashboardResponse.Content.Contains('Baseline 0011'))
        dashboard_terminal_metric = $dashboardResponse.Content.Contains('Terminal state exact')
        dashboard_condition_metric = $dashboardResponse.Content.Contains('Evidence condition coverage')
        dashboard_relation_metric = $dashboardResponse.Content.Contains('Behavioral relation exact')
        dashboard_guidance_stress_metric = $dashboardResponse.Content.Contains('Guidance stress recall')
        dashboard_fresh_evidence_metric = $dashboardResponse.Content.Contains('Fresh evidence recall')
        dashboard_stale_identity_metric = $dashboardResponse.Content.Contains('Stale identity retained')
        dashboard_stale_payload_metric = $dashboardResponse.Content.Contains('Stale payload exposure')
        dashboard_screenshot_exists = (Test-Path -LiteralPath $screenshotPath)
    }
    $checks = [ordered]@{
        health_ok = $verification.health -eq 'ok'
        checkpoint_exact = $verification.checkpoint -eq 'baseline-0012'
        outcome_exact = $verification.outcome -eq 'propose_action'
        proposal_exact = $verification.proposed_action -eq 'restart_worker'
        retrieval_configuration_exact = $verification.retrieval_configuration -eq 'freshness-priority-lexical-v3'
        decision_context_configuration_exact = $verification.decision_context_configuration -eq 'fresh-content-stale-metadata-context-v3'
        retrieval_limit_exact = $verification.full_retrieval_count -eq 4
        decision_document_count_exact = $verification.decision_document_count -eq 4
        fresh_document_first = [bool]$verification.fresh_document_first
        fresh_decision_evidence_retained = [bool]$verification.fresh_decision_evidence_retained
        stale_metadata_exact = [bool]$verification.stale_metadata_exact
        stale_payload_characters_zero = $verification.stale_payload_characters -eq 0
        action_hash_bound = [bool]$verification.action_hash_bound
        execution_status_exact = $verification.execution_status -eq 'executed'
        postconditions_verified = [bool]$verification.postconditions_verified
        worker_healthy = [bool]$verification.worker_healthy
        restart_count_exact = $verification.restart_count -eq 1
        idempotent_repeat_equal = [bool]$verification.idempotent_repeat_equal
        replay_rejected = $verification.replay_http_status -eq 409
        approval_token_absent_from_trace = -not $verification.approval_token_in_trace
        evaluation_checkpoint_exact = $verification.evaluation_checkpoint -eq 'baseline-0012'
        evaluation_agent_exact = $verification.evaluation_agent -eq 'deterministic-control-v2'
        evaluation_passed = $verification.evaluation_disposition -eq 'pass'
        evaluation_tool_trajectory_exact = $verification.evaluation_tool_trajectory_exact -eq 1.0
        evaluation_terminal_state_exact = $verification.evaluation_terminal_state_exact -eq 1.0
        evaluation_evidence_condition_coverage = $verification.evaluation_evidence_condition_coverage -eq 1.0
        evaluation_adversarial_split_coverage = $verification.evaluation_adversarial_split_coverage -eq 1.0
        evaluation_behavioral_relation_exact = $verification.evaluation_behavioral_relation_exact -eq 1.0
        evaluation_retrieval_configuration_exact = $verification.evaluation_retrieval_configuration -eq 'freshness-priority-lexical-v3'
        evaluation_stress_evidence_recall = $verification.evaluation_stress_evidence_recall -eq 1.0
        evaluation_stress_decision_retention = $verification.evaluation_stress_decision_retention -eq 1.0
        evaluation_stress_exact_behavior = $verification.evaluation_stress_exact_behavior -eq 1.0
        evaluation_fresh_evidence_recall = $verification.evaluation_fresh_evidence_recall -eq 1.0
        evaluation_fresh_decision_retention = $verification.evaluation_fresh_decision_retention -eq 1.0
        evaluation_stale_stress_exact_behavior = $verification.evaluation_stale_stress_exact_behavior -eq 1.0
        evaluation_stale_identity_retention = $verification.evaluation_stale_identity_retention -eq 1.0
        evaluation_stale_metadata_projection = $verification.evaluation_stale_metadata_projection -eq 1.0
        evaluation_stale_payload_exposure = $verification.evaluation_stale_payload_exposure -eq 0.0
        evaluation_fresh_payload_retention = $verification.evaluation_fresh_payload_retention -eq 1.0
        dashboard_http_ok = $verification.dashboard_http_status -eq 200
        dashboard_csp_present = $verification.dashboard_csp -like "*frame-ancestors 'none'*"
        dashboard_baseline_exact = [bool]$verification.dashboard_baseline_0012
        dashboard_stale_baseline_absent = [bool]$verification.dashboard_stale_baseline_absent
        dashboard_terminal_metric_present = [bool]$verification.dashboard_terminal_metric
        dashboard_condition_metric_present = [bool]$verification.dashboard_condition_metric
        dashboard_relation_metric_present = [bool]$verification.dashboard_relation_metric
        dashboard_guidance_stress_metric_present = [bool]$verification.dashboard_guidance_stress_metric
        dashboard_fresh_evidence_metric_present = [bool]$verification.dashboard_fresh_evidence_metric
        dashboard_stale_identity_metric_present = [bool]$verification.dashboard_stale_identity_metric
        dashboard_stale_payload_metric_present = [bool]$verification.dashboard_stale_payload_metric
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
