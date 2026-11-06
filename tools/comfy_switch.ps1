param([string]$to)
# Machine-specific example: edit the three install paths below for your machine. Switches ComfyUI between klein (images), h3 (video, music) and moss.
# comfy_switch.ps1 moss|klein|h3 (moss = 0.42 puerto 8190) : cierra todo ComfyUI y arranca el pedido (klein = 0.41 puerto 8189, h3 = 0.34 puerto 8188). Espera a que responda.
Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'main.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 8
if ($to -eq 'moss') {
  Start-Process -FilePath 'D:\ComfyUI_MOSS\ComfyUI_windows_portable\python_embeded\python.exe' -ArgumentList '-s','ComfyUI\main.py','--windows-standalone-build','--port','8190','--disable-auto-launch' -WorkingDirectory 'D:\ComfyUI_MOSS\ComfyUI_windows_portable' -WindowStyle Hidden
  $port = 8190
} elseif ($to -eq 'klein') {
  Start-Process -FilePath 'D:\ComfyUI_QI21\ComfyUI_windows_portable\python_embeded\python.exe' -ArgumentList '-s','ComfyUI\main.py','--windows-standalone-build','--port','8189' -WorkingDirectory 'D:\ComfyUI_QI21\ComfyUI_windows_portable' -WindowStyle Hidden
  $port = 8189
} else {
  Start-Process -FilePath 'D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\START_COMFY_H3_FAST.bat' -WorkingDirectory 'D:\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable' -WindowStyle Minimized
  $port = 8188
}
for ($i=0; $i -lt 120; $i++) { try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 "http://127.0.0.1:$port/system_stats" | Out-Null; "listo $to"; break } catch { Start-Sleep 5 } }
