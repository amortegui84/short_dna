param([string]$to)
# Machine-specific example: edit the install path below for your machine.
# comfy_switch.ps1 moss|klein|h3 : since 2026-11-10 there is ONE ComfyUI (0.45, port 8188) that serves Klein, MOSS, Qwen and H3.
# Nothing is closed or switched any more: this only makes sure that server is up and waits until it answers.
$port = 8188
$up = $false
try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:$port/system_stats" | Out-Null; $up = $true } catch {}
if (-not $up) {
  $running = Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'main.py' }
  if (-not $running) {
    Start-Process -FilePath 'D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\START_COMFY_H3_FAST.bat' -WorkingDirectory 'D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable' -WindowStyle Minimized
  }
}
for ($i=0; $i -lt 120; $i++) { try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:$port/system_stats" | Out-Null; "listo $to"; break } catch { Start-Sleep 5 } }