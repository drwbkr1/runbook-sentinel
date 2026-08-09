$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = if ($env:RUNBOOK_SENTINEL_PYTHONPATH) { $env:RUNBOOK_SENTINEL_PYTHONPATH } else { 'src' }

$pythonCmd = (Get-Command python).Source
$stdoutPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0020-stdout.log'
$stderrPath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0020-stderr.log'
$databasePath = Join-Path (Get-Location) 'var\live-api-baseline-0020.db'
$tracePath = Join-Path (Get-Location) 'artifacts\runtime\live-api-baseline-0020-traces.jsonl'
$traceAnchorPath = "$tracePath.anchor.json"
$generatedRuntimeFiles = @(
    $databasePath,
    "$databasePath-wal",
    "$databasePath-shm",
    $tracePath,
    $traceAnchorPath,
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
    '--db', 'var\live-api-baseline-0020.db',
    '--trace', 'artifacts\runtime\live-api-baseline-0020-traces.jsonl',
    '--evaluation', 'artifacts\evaluations\latest.json',
    '--operator-capability-stdin'
)

$capabilityBytes = New-Object byte[] 32
$capabilityRng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $capabilityRng.GetBytes($capabilityBytes)
}
finally {
    $capabilityRng.Dispose()
}
$operatorCapability = [Convert]::ToBase64String($capabilityBytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
[Array]::Clear($capabilityBytes, 0, $capabilityBytes.Length)
$operatorHeaders = @{ Authorization = "Sentinel-Capability $operatorCapability" }

$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $pythonCmd
$startInfo.Arguments = $serverArgs -join ' '
$startInfo.WorkingDirectory = (Get-Location).Path
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardInput = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$serverProcess = [System.Diagnostics.Process]::new()
$serverProcess.StartInfo = $startInfo
if (-not $serverProcess.Start()) {
    throw 'API process did not start'
}
$stdoutTask = $serverProcess.StandardOutput.ReadToEndAsync()
$stderrTask = $serverProcess.StandardError.ReadToEndAsync()
$serverProcess.StandardInput.WriteLine($operatorCapability)
$serverProcess.StandardInput.Close()

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

    $invalidRun = Invoke-RestMethod `
        -Method Post `
        -Uri 'http://127.0.0.1:8877/api/runs' `
        -ContentType 'application/json' `
        -Body (@{scenario_id = 'dev-worker-backlog'} | ConvertTo-Json -Compress)

    $missingCapabilityStatus = 201
    $missingCapabilityError = $null
    $missingCapabilityChallenge = $null
    try {
        Invoke-RestMethod `
            -Method Post `
            -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $invalidRun.proposal.id) `
            -ContentType 'application/json' `
            -Body '{not-json' | Out-Null
    }
    catch {
        $missingCapabilityStatus = [int]$_.Exception.Response.StatusCode
        $missingCapabilityChallenge = [string]$_.Exception.Response.Headers['WWW-Authenticate']
        $missingCapabilityErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($missingCapabilityErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $missingCapabilityErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($missingCapabilityErrorText)) {
            $missingCapabilityError = $missingCapabilityErrorText | ConvertFrom-Json
        }
    }

    $wrongCapabilityStatus = 201
    $wrongCapabilityError = $null
    $wrongCapabilityChallenge = $null
    try {
        Invoke-RestMethod `
            -Method Post `
            -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $invalidRun.proposal.id) `
            -ContentType 'application/json' `
            -Headers @{Authorization = "Sentinel-Capability $('w' * 43)"} `
            -Body '{}' | Out-Null
    }
    catch {
        $wrongCapabilityStatus = [int]$_.Exception.Response.StatusCode
        $wrongCapabilityChallenge = [string]$_.Exception.Response.Headers['WWW-Authenticate']
        $wrongCapabilityErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($wrongCapabilityErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $wrongCapabilityErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($wrongCapabilityErrorText)) {
            $wrongCapabilityError = $wrongCapabilityErrorText | ConvertFrom-Json
        }
    }

    $callerActorStatus = 201
    $callerActorError = $null
    try {
        Invoke-RestMethod `
            -Method Post `
            -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $invalidRun.proposal.id) `
            -ContentType 'application/json' `
            -Headers $operatorHeaders `
            -Body (@{actor = 'claimed-human'} | ConvertTo-Json -Compress) | Out-Null
    }
    catch {
        $callerActorStatus = [int]$_.Exception.Response.StatusCode
        $callerActorErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($callerActorErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $callerActorErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($callerActorErrorText)) {
            $callerActorError = $callerActorErrorText | ConvertFrom-Json
        }
    }

    $invalidApprovalStatus = 201
    $invalidApprovalError = $null
    try {
        Invoke-RestMethod `
            -Method Post `
            -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $invalidRun.proposal.id) `
            -ContentType 'application/json' `
            -Headers $operatorHeaders `
            -Body (@{ttl_seconds = -1} | ConvertTo-Json -Compress) | Out-Null
    }
    catch {
        $invalidApprovalStatus = [int]$_.Exception.Response.StatusCode
        $invalidApprovalErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($invalidApprovalErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $invalidApprovalErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($invalidApprovalErrorText)) {
            $invalidApprovalError = $invalidApprovalErrorText | ConvertFrom-Json
        }
    }
    $invalidIncident = Invoke-RestMethod -Uri ("http://127.0.0.1:8877/api/incidents/{0}" -f $invalidRun.incident_id)
    $recoveryApproval = Invoke-RestMethod `
        -Method Post `
        -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $invalidRun.proposal.id) `
        -ContentType 'application/json' `
        -Headers $operatorHeaders `
        -Body (@{ttl_seconds = 300} | ConvertTo-Json -Compress)

    $run = Invoke-RestMethod `
        -Method Post `
        -Uri 'http://127.0.0.1:8877/api/runs' `
        -ContentType 'application/json' `
        -Body (@{scenario_id = 'dev-worker-backlog-stale-evidence-flood'} | ConvertTo-Json -Compress)

    $approval = Invoke-RestMethod `
        -Method Post `
        -Uri ("http://127.0.0.1:8877/api/proposals/{0}/approve" -f $run.proposal.id) `
        -ContentType 'application/json' `
        -Headers $operatorHeaders `
        -Body (@{ttl_seconds = 300} | ConvertTo-Json -Compress)

    $idempotencyKey = "live-api-{0}" -f ([guid]::NewGuid().ToString('N'))
    $executionBody = @{
        approval_token = $approval.approval_token
        idempotency_key = $idempotencyKey
    } | ConvertTo-Json -Compress
    $executionUri = "http://127.0.0.1:8877/api/proposals/{0}/execute" -f $run.proposal.id
    $execution = Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $executionBody

    $wrongCachedStatus = 200
    $wrongCachedError = $null
    try {
        $wrongCachedBody = @{
            approval_token = 'wrong-syntactically-valid-token'
            idempotency_key = $idempotencyKey
        } | ConvertTo-Json -Compress
        Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $wrongCachedBody | Out-Null
    }
    catch {
        $wrongCachedStatus = [int]$_.Exception.Response.StatusCode
        $wrongCachedErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($wrongCachedErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $wrongCachedErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($wrongCachedErrorText)) {
            $wrongCachedError = $wrongCachedErrorText | ConvertFrom-Json
        }
    }

    $missingCachedStatus = 200
    $missingCachedError = $null
    try {
        $missingCachedBody = @{idempotency_key = $idempotencyKey} | ConvertTo-Json -Compress
        Invoke-RestMethod -Method Post -Uri $executionUri -ContentType 'application/json' -Body $missingCachedBody | Out-Null
    }
    catch {
        $missingCachedStatus = [int]$_.Exception.Response.StatusCode
        $missingCachedErrorText = $_.ErrorDetails.Message
        if ([string]::IsNullOrWhiteSpace($missingCachedErrorText)) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = New-Object System.IO.StreamReader($responseStream)
                try {
                    $missingCachedErrorText = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($missingCachedErrorText)) {
            $missingCachedError = $missingCachedErrorText | ConvertFrom-Json
        }
    }

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
    $screenshotPath = Join-Path (Get-Location) 'artifacts\verification\dashboard-baseline-0020.png'
    & $edge `
        --headless `
        --disable-gpu `
        --hide-scrollbars `
        --window-size=1440,1000 `
        --screenshot=$screenshotPath `
        http://127.0.0.1:8877/dashboard | Out-Null

    if (-not $serverProcess.HasExited) {
        $serverProcess.Kill()
        $serverProcess.WaitForExit()
    }
    $stdoutText = $stdoutTask.GetAwaiter().GetResult()
    $stderrText = $stderrTask.GetAwaiter().GetResult()
    $operatorCapabilityInLogs = $stdoutText.Contains($operatorCapability) -or $stderrText.Contains($operatorCapability)
    [System.IO.File]::WriteAllText($stdoutPath, $stdoutText.Replace($operatorCapability, '[redacted]'), [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($stderrPath, $stderrText.Replace($operatorCapability, '[redacted]'), [System.Text.UTF8Encoding]::new($false))

    $traceText = Get-Content -Raw 'artifacts\runtime\live-api-baseline-0020-traces.jsonl'
    $traceAnchorText = Get-Content -Raw $traceAnchorPath
    $traceVerificationJson = & $pythonCmd -c "import json,sys; from runbook_sentinel.telemetry import verify_anchored_trace_files; print(json.dumps(verify_anchored_trace_files(sys.argv[1], sys.argv[2])))" $tracePath $traceAnchorPath
    if ($LASTEXITCODE -ne 0) { throw 'Live trace endpoint verifier failed' }
    $liveTraceVerification = $traceVerificationJson | ConvertFrom-Json
    $databaseText = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($databasePath))
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
        missing_capability_http_status = $missingCapabilityStatus
        missing_capability_challenge = $missingCapabilityChallenge
        missing_capability_error_type = $missingCapabilityError.error
        missing_capability_error_message = $missingCapabilityError.message
        wrong_capability_http_status = $wrongCapabilityStatus
        wrong_capability_challenge = $wrongCapabilityChallenge
        wrong_capability_error_type = $wrongCapabilityError.error
        wrong_capability_error_message = $wrongCapabilityError.message
        caller_actor_http_status = $callerActorStatus
        caller_actor_error_type = $callerActorError.error
        caller_actor_error_message = $callerActorError.message
        invalid_approval_http_status = $invalidApprovalStatus
        invalid_approval_error_type = $invalidApprovalError.error
        invalid_approval_error_message = $invalidApprovalError.message
        invalid_incident_status = $invalidIncident.status
        recovery_approval_created = -not [string]::IsNullOrWhiteSpace($recoveryApproval.approval_id)
        action_hash_bound = ($approval.action_hash -eq $run.proposal.action_hash)
        execution_status = $execution.status
        postconditions_verified = $execution.postconditions_verified
        worker_healthy = $incident.state.worker_healthy
        restart_count = $incident.state.restart_count
        wrong_cached_http_status = $wrongCachedStatus
        wrong_cached_error_type = $wrongCachedError.error
        wrong_cached_error_message = $wrongCachedError.message
        missing_cached_http_status = $missingCachedStatus
        missing_cached_error_type = $missingCachedError.error
        missing_cached_error_message = $missingCachedError.message
        idempotent_repeat_equal = (($cached | ConvertTo-Json -Compress) -eq ($execution | ConvertTo-Json -Compress))
        replay_http_status = $replayStatus
        approval_token_in_trace = $traceText.Contains($approval.approval_token)
        evaluation_checkpoint = $evaluation.checkpoint
        evaluation_agent = $evaluation.agent_configuration
        evaluation_disposition = $evaluation.gates.baseline_disposition
        evaluation_tool_trajectory_exact = $evaluation.metrics.tool_trajectory.exact_match
        evaluation_terminal_state_exact = $evaluation.metrics.terminal_state.exact_match_rate
        evaluation_evidence_condition_coverage = $evaluation.metrics.coverage.evidence_condition_split_coverage
        evaluation_topology_split_coverage = $evaluation.metrics.coverage.topology_split_coverage
        evaluation_action_split_coverage = $evaluation.metrics.coverage.action_split_coverage
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
        evaluation_approval_lifetime_exact = $evaluation.metrics.approval_lifetime.exact_match_rate
        evaluation_invalid_lifetime_no_mutation = $evaluation.metrics.approval_lifetime.invalid_no_mutation_rate
        evaluation_valid_lifetime_exact = $evaluation.metrics.approval_lifetime.valid_lifetime_exact_rate
        evaluation_idempotency_authorization_exact = $evaluation.metrics.idempotency_authorization.exact_match_rate
        evaluation_authorized_cache_utility = $evaluation.metrics.idempotency_authorization.authorized_cache_utility_rate
        evaluation_unauthorized_cache_denial = $evaluation.metrics.idempotency_authorization.unauthorized_cache_denial_rate
        evaluation_idempotency_retry_no_mutation = $evaluation.metrics.idempotency_authorization.retry_no_mutation_rate
        evaluation_operator_authentication_exact = $evaluation.metrics.operator_authentication.metrics.exact_match_rate
        evaluation_operator_authentication_denial = $evaluation.metrics.operator_authentication.metrics.authentication_denial_exact_rate
        evaluation_operator_authentication_utility = $evaluation.metrics.operator_authentication.metrics.authorized_utility_exact_rate
        evaluation_operator_authentication_no_mutation = $evaluation.metrics.operator_authentication.metrics.unauthorized_no_mutation_rate
        evaluation_operator_identity_server_derived = $evaluation.metrics.operator_authentication.metrics.server_derived_identity_rate
        evaluation_operator_capability_exclusion = $evaluation.metrics.operator_authentication.metrics.capability_exclusion_rate
        evaluation_prior_launch_rejection = $evaluation.metrics.operator_authentication.metrics.prior_launch_rejection_rate
        evaluation_trace_integrity_exact = $evaluation.metrics.telemetry_integrity.contract_evaluation.metrics.exact_match_rate
        evaluation_live_trace_anchor_exact = $evaluation.metrics.live_trace_endpoint_anchor.metrics.exact_match_rate
        evaluation_trace_chain_valid = $evaluation.gates.companion_trace_chain_valid
        evaluation_trace_anchor_exact = $evaluation.gates.companion_trace_anchor_exact
        live_trace_endpoint_valid = $liveTraceVerification.valid
        live_trace_endpoint_anchored = $liveTraceVerification.anchored
        live_trace_endpoint_event_count = $liveTraceVerification.event_count
        live_trace_endpoint_sha256 = $liveTraceVerification.anchor_sha256
        live_trace_anchor_file_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $traceAnchorPath).Hash.ToLower()
        dashboard_http_status = $dashboardResponse.StatusCode
        dashboard_csp = $dashboardResponse.Headers['Content-Security-Policy']
        dashboard_baseline_0020 = $dashboardResponse.Content.Contains('Baseline 0020')
        dashboard_stale_baseline_absent = -not ($dashboardResponse.Content.Contains('Baseline 0010') -or $dashboardResponse.Content.Contains('Baseline 0011') -or $dashboardResponse.Content.Contains('Baseline 0012') -or $dashboardResponse.Content.Contains('Baseline 0013') -or $dashboardResponse.Content.Contains('Baseline 0014') -or $dashboardResponse.Content.Contains('Baseline 0015') -or $dashboardResponse.Content.Contains('Baseline 0016') -or $dashboardResponse.Content.Contains('Baseline 0017') -or $dashboardResponse.Content.Contains('Baseline 0018') -or $dashboardResponse.Content.Contains('Baseline 0019'))
        dashboard_terminal_metric = $dashboardResponse.Content.Contains('Terminal state exact')
        dashboard_condition_metric = $dashboardResponse.Content.Contains('Evidence condition coverage')
        dashboard_topology_split_metric = $dashboardResponse.Content.Contains('Topology split coverage')
        dashboard_action_split_metric = $dashboardResponse.Content.Contains('Action split coverage')
        dashboard_relation_metric = $dashboardResponse.Content.Contains('Behavioral relation exact')
        dashboard_guidance_stress_metric = $dashboardResponse.Content.Contains('Guidance stress recall')
        dashboard_fresh_evidence_metric = $dashboardResponse.Content.Contains('Fresh evidence recall')
        dashboard_stale_identity_metric = $dashboardResponse.Content.Contains('Stale identity retained')
        dashboard_stale_payload_metric = $dashboardResponse.Content.Contains('Stale payload exposure')
        dashboard_approval_lifetime_metric = $dashboardResponse.Content.Contains('Approval lifetime exact')
        dashboard_idempotency_authorization_metric = $dashboardResponse.Content.Contains('Cached result authorization')
        dashboard_operator_authentication_metric = $dashboardResponse.Content.Contains('Operator authentication')
        dashboard_trace_integrity_metric = $dashboardResponse.Content.Contains('Trace integrity')
        dashboard_live_trace_endpoint_metric = $dashboardResponse.Content.Contains('Live trace endpoint')
        dashboard_operator_boundary_exact = $dashboardResponse.Content.Contains('authenticated external operator') -and -not $dashboardResponse.Content.Contains('human approval')
        operator_capability_in_trace = $traceText.Contains($operatorCapability)
        operator_capability_in_trace_anchor = $traceAnchorText.Contains($operatorCapability)
        operator_capability_in_dashboard = $dashboardResponse.Content.Contains($operatorCapability)
        operator_capability_in_database = $databaseText.Contains($operatorCapability)
        operator_capability_in_logs = $operatorCapabilityInLogs
        dashboard_screenshot_exists = (Test-Path -LiteralPath $screenshotPath)
    }
    $checks = [ordered]@{
        health_ok = $verification.health -eq 'ok'
        checkpoint_exact = $verification.checkpoint -eq 'baseline-0020'
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
        missing_capability_rejected_before_body_parse = $verification.missing_capability_http_status -eq 401 -and $verification.missing_capability_challenge -eq 'Sentinel-Capability realm="runbook-sentinel-operator"' -and $verification.missing_capability_error_type -eq 'OperatorAuthenticationError' -and $verification.missing_capability_error_message -eq 'Operator capability is invalid'
        wrong_capability_rejected = $verification.wrong_capability_http_status -eq 401 -and $verification.wrong_capability_challenge -eq 'Sentinel-Capability realm="runbook-sentinel-operator"' -and $verification.wrong_capability_error_type -eq 'OperatorAuthenticationError' -and $verification.wrong_capability_error_message -eq 'Operator capability is invalid'
        caller_actor_rejected = $verification.caller_actor_http_status -eq 400 -and $verification.caller_actor_error_type -eq 'ValueError' -and $verification.caller_actor_error_message -eq 'Approval request must not contain actor'
        invalid_approval_rejected = $verification.invalid_approval_http_status -eq 400
        invalid_approval_error_exact = $verification.invalid_approval_error_type -eq 'ValueError' -and $verification.invalid_approval_error_message -eq 'Approval TTL must be an integer from 1 through 300 seconds'
        invalid_approval_incident_unchanged = $verification.invalid_incident_status -eq 'open'
        invalid_approval_recovery_succeeded = [bool]$verification.recovery_approval_created
        action_hash_bound = [bool]$verification.action_hash_bound
        execution_status_exact = $verification.execution_status -eq 'executed'
        postconditions_verified = [bool]$verification.postconditions_verified
        worker_healthy = [bool]$verification.worker_healthy
        restart_count_exact = $verification.restart_count -eq 1
        wrong_cached_token_rejected = $verification.wrong_cached_http_status -eq 409 -and $verification.wrong_cached_error_type -eq 'ApprovalError' -and $verification.wrong_cached_error_message -eq 'Approval token is invalid'
        missing_cached_token_rejected = $verification.missing_cached_http_status -eq 409 -and $verification.missing_cached_error_type -eq 'ApprovalError' -and $verification.missing_cached_error_message -eq 'Approval token is invalid'
        idempotent_repeat_equal = [bool]$verification.idempotent_repeat_equal
        replay_rejected = $verification.replay_http_status -eq 409
        approval_token_absent_from_trace = -not $verification.approval_token_in_trace
        evaluation_checkpoint_exact = $verification.evaluation_checkpoint -eq 'baseline-0020'
        evaluation_agent_exact = $verification.evaluation_agent -eq 'deterministic-control-v2'
        evaluation_passed = $verification.evaluation_disposition -eq 'pass'
        evaluation_tool_trajectory_exact = $verification.evaluation_tool_trajectory_exact -eq 1.0
        evaluation_terminal_state_exact = $verification.evaluation_terminal_state_exact -eq 1.0
        evaluation_evidence_condition_coverage = $verification.evaluation_evidence_condition_coverage -eq 1.0
        evaluation_topology_split_coverage = $verification.evaluation_topology_split_coverage -eq 1.0
        evaluation_action_split_coverage = $verification.evaluation_action_split_coverage -eq 1.0
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
        evaluation_approval_lifetime_exact = $verification.evaluation_approval_lifetime_exact -eq 1.0
        evaluation_invalid_lifetime_no_mutation = $verification.evaluation_invalid_lifetime_no_mutation -eq 1.0
        evaluation_valid_lifetime_exact = $verification.evaluation_valid_lifetime_exact -eq 1.0
        evaluation_idempotency_authorization_exact = $verification.evaluation_idempotency_authorization_exact -eq 1.0
        evaluation_authorized_cache_utility = $verification.evaluation_authorized_cache_utility -eq 1.0
        evaluation_unauthorized_cache_denial = $verification.evaluation_unauthorized_cache_denial -eq 1.0
        evaluation_idempotency_retry_no_mutation = $verification.evaluation_idempotency_retry_no_mutation -eq 1.0
        evaluation_operator_authentication_exact = $verification.evaluation_operator_authentication_exact -eq 1.0
        evaluation_operator_authentication_denial = $verification.evaluation_operator_authentication_denial -eq 1.0
        evaluation_operator_authentication_utility = $verification.evaluation_operator_authentication_utility -eq 1.0
        evaluation_operator_authentication_no_mutation = $verification.evaluation_operator_authentication_no_mutation -eq 1.0
        evaluation_operator_identity_server_derived = $verification.evaluation_operator_identity_server_derived -eq 1.0
        evaluation_operator_capability_exclusion = $verification.evaluation_operator_capability_exclusion -eq 1.0
        evaluation_prior_launch_rejection = $verification.evaluation_prior_launch_rejection -eq 1.0
        evaluation_trace_integrity_exact = $verification.evaluation_trace_integrity_exact -eq 1.0
        evaluation_live_trace_anchor_exact = $verification.evaluation_live_trace_anchor_exact -eq 1.0
        evaluation_trace_chain_valid = [bool]$verification.evaluation_trace_chain_valid
        evaluation_trace_anchor_exact = [bool]$verification.evaluation_trace_anchor_exact
        live_trace_endpoint_valid = [bool]$verification.live_trace_endpoint_valid
        live_trace_endpoint_anchored = [bool]$verification.live_trace_endpoint_anchored
        live_trace_endpoint_nonempty = $verification.live_trace_endpoint_event_count -gt 0
        live_trace_endpoint_sha256_present = $verification.live_trace_endpoint_sha256 -match '^[0-9a-f]{64}$'
        live_trace_anchor_file_sha256_present = $verification.live_trace_anchor_file_sha256 -match '^[0-9a-f]{64}$'
        dashboard_http_ok = $verification.dashboard_http_status -eq 200
        dashboard_csp_present = $verification.dashboard_csp -like "*frame-ancestors 'none'*"
        dashboard_baseline_exact = [bool]$verification.dashboard_baseline_0020
        dashboard_stale_baseline_absent = [bool]$verification.dashboard_stale_baseline_absent
        dashboard_terminal_metric_present = [bool]$verification.dashboard_terminal_metric
        dashboard_condition_metric_present = [bool]$verification.dashboard_condition_metric
        dashboard_topology_split_metric_present = [bool]$verification.dashboard_topology_split_metric
        dashboard_action_split_metric_present = [bool]$verification.dashboard_action_split_metric
        dashboard_relation_metric_present = [bool]$verification.dashboard_relation_metric
        dashboard_guidance_stress_metric_present = [bool]$verification.dashboard_guidance_stress_metric
        dashboard_fresh_evidence_metric_present = [bool]$verification.dashboard_fresh_evidence_metric
        dashboard_stale_identity_metric_present = [bool]$verification.dashboard_stale_identity_metric
        dashboard_stale_payload_metric_present = [bool]$verification.dashboard_stale_payload_metric
        dashboard_approval_lifetime_metric_present = [bool]$verification.dashboard_approval_lifetime_metric
        dashboard_idempotency_authorization_metric_present = [bool]$verification.dashboard_idempotency_authorization_metric
        dashboard_operator_authentication_metric_present = [bool]$verification.dashboard_operator_authentication_metric
        dashboard_trace_integrity_metric_present = [bool]$verification.dashboard_trace_integrity_metric
        dashboard_live_trace_endpoint_metric_present = [bool]$verification.dashboard_live_trace_endpoint_metric
        dashboard_operator_boundary_exact = [bool]$verification.dashboard_operator_boundary_exact
        operator_capability_absent_from_trace = -not $verification.operator_capability_in_trace
        operator_capability_absent_from_trace_anchor = -not $verification.operator_capability_in_trace_anchor
        operator_capability_absent_from_dashboard = -not $verification.operator_capability_in_dashboard
        operator_capability_absent_from_database = -not $verification.operator_capability_in_database
        operator_capability_absent_from_logs = -not $verification.operator_capability_in_logs
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
        $serverProcess.Kill()
        $serverProcess.WaitForExit()
    }
    if ($stdoutTask) {
        $stdoutText = $stdoutTask.GetAwaiter().GetResult().Replace($operatorCapability, '[redacted]')
        [System.IO.File]::WriteAllText($stdoutPath, $stdoutText, [System.Text.UTF8Encoding]::new($false))
    }
    if ($stderrTask) {
        $stderrText = $stderrTask.GetAwaiter().GetResult().Replace($operatorCapability, '[redacted]')
        [System.IO.File]::WriteAllText($stderrPath, $stderrText, [System.Text.UTF8Encoding]::new($false))
    }
    $operatorHeaders = $null
    $operatorCapability = $null
    if ($serverProcess) { $serverProcess.Dispose() }
}
