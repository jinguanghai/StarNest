import subprocess
import json
import sys
import os
import tempfile
import base64
import ctypes
import threading
import time
import queue
import re

class SpeechRecognitionError(Exception):
    pass

class SpeechSynthesisError(Exception):
    pass

def _run_powershell(script):
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        if result.returncode != 0:
            raise SpeechRecognitionError(f"PowerShell error: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise SpeechRecognitionError("PowerShell timeout")
    except FileNotFoundError:
        raise SpeechRecognitionError("PowerShell not found")

def yuyin_shuru():
    ps_script = """
    Add-Type -AssemblyName System.Speech
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognizer
    $recognizer.SetInputToDefaultAudioDevice()
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    $result = $recognizer.Recognize()
    if ($result -ne $null) {
        $text = $result.Text
        $confidence = $result.Confidence
        $json = @{text=$text; confidence=$confidence} | ConvertTo-Json -Compress
        Write-Output $json
    } else {
        Write-Output '{"text":"","confidence":0}'
    }
    """
    try:
        output = _run_powershell(ps_script)
        data = json.loads(output)
        return {
            "text": data.get("text", ""),
            "confidence": data.get("confidence", 0.0),
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": str(e)
        }

def yuyin_shuchu(text):
    if not isinstance(text, str) or not text.strip():
        return {
            "success": False,
            "error": "Empty text"
        }
    
    safe_text = text.replace('"', '\\"').replace("'", "''")
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synthesizer.Speak("{safe_text}")
    """
    try:
        _run_powershell(ps_script)
        return {
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def yuyin_shuru_async(timeout=5):
    result_queue = queue.Queue()
    
    def _recognize_thread():
        result = yuyin_shuru()
        result_queue.put(result)
    
    thread = threading.Thread(target=_recognize_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": "Timeout"
        }
    
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return {
            "text": "",
            "confidence": 0.0,
            "success": False,
            "error": "No result"
        }

def yuyin_shuchu_async(text, callback=None):
    def _speak_thread():
        result = yuyin_shuchu(text)
        if callback:
            callback(result)
    
    thread = threading.Thread(target=_speak_thread, daemon=True)
    thread.start()
    return thread

def get_available_voices():
    ps_script = """
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $voices = $synthesizer.GetInstalledVoices()
    $voiceList = @()
    foreach ($voice in $voices) {
        $info = $voice.VoiceInfo
        $voiceList += @{
            name=$info.Name;
            culture=$info.Culture.Name;
            gender=$info.Gender.ToString();
            age=$info.Age.ToString()
        }
    }
    $voiceList | ConvertTo-Json -Compress
    """
    try:
        output = _run_powershell(ps_script)
        return json.loads(output)
    except Exception as e:
        return []

def set_voice(voice_name):
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $voice = $synthesizer.GetInstalledVoices() | Where-Object {{ $_.VoiceInfo.Name -eq "{voice_name}" }}
    if ($voice -ne $null) {{
        $synthesizer.SelectVoice("{voice_name}")
        Write-Output "OK"
    }} else {{
        Write-Output "NOT_FOUND"
    }}
    """
    try:
        output = _run_powershell(ps_script)
        return output == "OK"
    except:
        return False

def set_volume(volume):
    volume = max(0, min(100, int(volume)))
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synthesizer.Volume = {volume}
    """
    try:
        _run_powershell(ps_script)
        return True
    except:
        return False

def set_rate(rate):
    rate = max(-10, min(10, int(rate)))
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synthesizer.Rate = {rate}
    """
    try:
        _run_powershell(ps_script)
        return True
    except:
        return False

def is_speech_available():
    try:
        _run_powershell("Add-Type -AssemblyName System.Speech; Write-Output 'OK'")
        return True
    except:
        return False

def yuyin_shuru_to_file(filepath):
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognizer
    $recognizer.SetInputToDefaultAudioDevice()
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    $result = $recognizer.Recognize()
    if ($result -ne $null) {{
        $text = $result.Text
        $confidence = $result.Confidence
        $data = @{{text=$text; confidence=$confidence; timestamp=(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')}}
        $data | ConvertTo-Json | Out-File -FilePath "{filepath}" -Encoding UTF8
        Write-Output "OK"
    }} else {{
        Write-Output "NO_SPEECH"
    }}
    """
    try:
        output = _run_powershell(ps_script)
        return output == "OK"
    except:
        return False

def yuyin_shuchu_to_file(text, filepath):
    safe_text = text.replace('"', '\\"')
    ps_script = f"""
    Add-Type -AssemblyName System.Speech
    $synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synthesizer.SetOutputToWaveFile("{filepath}")
    $synthesizer.Speak("{safe_text}")
    $synthesizer.Dispose()
    Write-Output "OK"
    """
    try:
        output = _run_powershell(ps_script)
        return output == "OK"
    except:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "recognize":
            result = yuyin_shuru()
            print(json.dumps(result, ensure_ascii=False))
        elif command == "speak":
            if len(sys.argv) > 2:
                text = " ".join(sys.argv[2:])
                result = yuyin_shuchu(text)
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(json.dumps({"success": False, "error": "No text provided"}))
        elif command == "available":
            voices = get_available_voices()
            print(json.dumps(voices, ensure_ascii=False))
        elif command == "check":
            print(json.dumps({"available": is_speech_available()}))
        else:
            print(json.dumps({"success": False, "error": f"Unknown command: {command}"}))
    else:
        print("语音识别工具 - Windows System.Speech PowerShell调用")
        print("用法:")
        print("  python yuyin_gongju.py recognize          - 语音识别")
        print("  python yuyin_gongju.py speak <文本>       - 语音合成")
        print("  python yuyin_gongju.py available          - 列出可用语音")
        print("  python yuyin_gongju.py check              - 检查语音功能可用性")