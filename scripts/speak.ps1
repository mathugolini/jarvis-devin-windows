param([Parameter(Mandatory=$true)][string]$TextPath, [string]$Voice = "")
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$Synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($Voice) {
        $Synth.SelectVoice($Voice)
    } else {
        $Brazilian = $Synth.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -eq "pt-BR" } | Select-Object -First 1
        if ($Brazilian) { $Synth.SelectVoice($Brazilian.VoiceInfo.Name) }
    }
    $Text = [IO.File]::ReadAllText($TextPath, [Text.Encoding]::UTF8)
    $Synth.Speak($Text)
} finally {
    $Synth.Dispose()
}
