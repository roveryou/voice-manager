# 🖥️ Discord PC Control Bot

Steuere deinen Windows-PC über Discord Slash-Commands.

## ⚡ Installation

1. **Python installieren** (3.8+): https://python.org
2. **Discord Bot erstellen**: https://discord.com/developers/applications
3. **Bot-Token** kopieren und in `config.py` einfügen
4. **Deine Discord-ID** in `config.py` eintragen
5. `installer.bat` ausführen
6. Bot in deinen Server einladen

## 🔧 Discord Bot Setup

1. Gehe zu https://discord.com/developers/applications
2. Klicke "New Application"
3. Gehe zu "Bot" → "Add Bot"
4. Aktiviere unter "Privileged Gateway Intents":
   - ✅ Message Content Intent
5. Kopiere den Token
6. Unter "OAuth2" → "URL Generator":
   - Scopes: `bot` + `applications.commands`
   - Berechtigungen: `Send Messages`, `Read Messages`, `Embed Links`
   - URL öffnen und Bot in deinen Server einladen

## 🚀 Start

Einfach `python main.py` ausführen oder PC neustarten (Autostart ist aktiv).

## ⚠️ Wichtig

- **Token geheim halten!** Niemanden teilen.
- Nur auf deinem eigenen PC verwenden!
