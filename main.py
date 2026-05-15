import discord
import asyncio

tokens = [
    "MTUwNDc2Nzk0NzY2MTUwODYzOA.GqnpDv.lgosXBS7YoxPa3iJfuOOK77qpdW2V3BakFICas",
    "MTUwNDc2NjA0NzI4MDk1OTUwOQ.GT6Nli.BYFlaG-HtsbkVIqh8GizU1Pmbk7YmtvgsUQGAQ",
    "MTUwNDc4NzQ4MDYxMDg2NTE2Mg.Gcn4aO.LK68YECmiwIug5pa8poKdNl1spbJ2uL2ZL6Edw",
]

GUILD_ID = 1500305759337058334

# Channel-IDs für die Verteilung
VOICE_CHANNEL_IDS = [
    1500306899239702538,  # public
    1500306884454777015,  # trio
    1500306876645118002,  # squad
]

# Maximale User pro Channel bevor ein anderer Channel gewählt wird
MAX_USERS_PER_CHANNEL = 5

# Speichert den zugewiesenen Channel für jeden Token
token_channel_map = {}

async def find_least_full_channel(guild):
    """Findet den Channel mit den wenigsten Usern"""
    best_channel = None
    least_users = float('inf')
    
    for channel_id in VOICE_CHANNEL_IDS:
        channel = guild.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            continue
        
        # Zähle die Member im Channel (nur echte User, keine Bots)
        member_count = sum(1 for m in channel.members if not m.bot)
        
        # Prüfe ob Bot-Limit erreicht ist
        bot_count = sum(1 for m in channel.members if m.bot)
        
        print(f"  Channel {channel.name}: {member_count} User, {bot_count} Bots")
        
        if member_count < least_users and member_count < MAX_USERS_PER_CHANNEL:
            least_users = member_count
            best_channel = channel
        elif best_channel is None:
            best_channel = channel
    
    return best_channel

def get_channel_for_token(index):
    """Feste Verteilung (Fallback)"""
    return VOICE_CHANNEL_IDS[index % len(VOICE_CHANNEL_IDS)]

async def join_voice(token, index):
    client = discord.Client()
    
    @client.event
    async def on_ready():
        print(f"\n=== {client.user} ist eingeloggt ===")
        
        guild = client.get_guild(GUILD_ID)
        if not guild:
            print(f"⚠️ {client.user}: Server mit ID {GUILD_ID} nicht gefunden!")
            print(f"   → Account ist wahrscheinlich nicht auf diesem Server.")
            print(f"   → Warte 60 Sekunden und versuche es erneut...")
            await client.close()
            return
        
        # Finde den am wenigsten vollen Channel
        channel = await find_least_full_channel(guild)
        
        if not channel:
            print(f"❌ {client.user}: Kein passender Voice-Channel gefunden")
            await client.close()
            return
        
        # Speichere zugewiesenen Channel
        token_channel_map[token] = channel.id
        
        print(f"  → Versuche {channel.name} zu joinen...")
        
        try:
            if client.voice_clients:
                vc = client.voice_clients[0]
                if vc.channel.id != channel.id:
                    await vc.disconnect()
                    await asyncio.sleep(1)
                    await channel.connect()
                    print(f"  ✅ {client.user} ist zu {channel.name} gewechselt")
                else:
                    print(f"  ✅ {client.user} ist bereits in {channel.name}")
            else:
                await channel.connect()
                print(f"  ✅ {client.user} ist {channel.name} beigetreten")
        except discord.Forbidden:
            print(f"❌ {client.user}: Keine Berechtigung für {channel.name}")
        except Exception as e:
            print(f"❌ {client.user}: Fehler beim Joinen: {e}")
    
    @client.event
    async def on_voice_state_update(member, before, after):
        if member.id != client.user.id:
            return
        
        guild = client.get_guild(GUILD_ID)
        if not guild:
            return
        
        # Disconnect
        if before.channel is not None and after.channel is None:
            print(f"\n🔄 {client.user}: wurde aus {before.channel.name} disconnected. Reconnecte...")
            await asyncio.sleep(3)
            
            # Finde den aktuell am wenigsten vollen Channel
            channel = await find_least_full_channel(guild)
            if channel:
                try:
                    await channel.connect()
                    token_channel_map[token] = channel.id
                    print(f"  ✅ {client.user} ist wieder in {channel.name} gejoint")
                except Exception as e:
                    print(f"  ❌ Fehler beim Reconnect: {e}")
        
        # Wurde in anderen Channel verschoben
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            old_channel = before.channel.name
            new_channel = after.channel.name
            print(f"  🔀 {client.user}: {old_channel} → {new_channel}")
    
    try:
        await client.start(token)
    except discord.LoginFailure:
        print(f"\n❌ Token für Account {index+1} ist ungültig!")
    except Exception as e:
        print(f"\n❌ Verbindungsfehler bei Account {index+1}: {e}")
        raise  # Wird von keep_connected abgefangen

async def keep_connected(token, index):
    """Automatischer Neustart bei Fehlern"""
    retry_count = 0
    while True:
        try:
            await join_voice(token, index)
        except Exception as e:
            retry_count += 1
            wait_time = min(10 * retry_count, 60)  # Max 60 Sekunden warten
            print(f"🔄 Account {index+1}: Neustart in {wait_time}s (Versuch {retry_count})...")
            await asyncio.sleep(wait_time)

async def main():
    print("🚀 Starte Discord Voice-Manager...")
    print(f"   Server ID: {GUILD_ID}")
    print(f"   Channels: {VOICE_CHANNEL_IDS}")
    print(f"   Max User pro Channel: {MAX_USERS_PER_CHANNEL}")
    print()
    
    tasks = []
    for i, token in enumerate(tokens):
        tasks.append(keep_connected(token, i))
    
    await asyncio.gather(*tasks)

asyncio.run(main())
