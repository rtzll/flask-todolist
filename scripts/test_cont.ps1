$count = 0
do {
    $count++
    Write-Output  "[$env:STAGE_NAME] Staring container [Attempt: $count]"
    $testStart = Invoke-WebRequest -Uri http://localhost:8000

    if ($testStart.statuscode -eq '200') {
        $started = $true 
    } else {
        Start-Sleep -Seconds 1
    }
} until ($started -or ($count -eq 3))

if (!$started) {
    exit 1
} 
