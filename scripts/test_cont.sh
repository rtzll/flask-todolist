    count = 0
    $count++
    echo "[$env:STAGE_NAME] Staring container [Attempt: $count]"
    $testStart = Invoke-WebRequest -Uri http://localhost:8000

    if ($testStart.statuscode -eq '200') {
        $started = $true 
    } else {
        Start-Sleep -Seconds 1
    }

    if (!$started) {
    exit 1
    } 
