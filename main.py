import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

HF_REQUIREMENT = 24
MAX_PLAYERS = 8
HOST_USERNAME = "TheRealGreen129"
HOST_DISPLAY = "green"
PRIVATE_SERVER_LINK = "PUT_YOUR_PRIVATE_SERVER_LINK_HERE"

# Queue storage
queue = []

class RunView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Private Server", style=discord.ButtonStyle.green)
    async def join_server(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"🔗 Join here: {PRIVATE_SERVER_LINK}",
            ephemeral=True
        )

    @discord.ui.button(label="Ping Me When Starting", style=discord.ButtonStyle.blurple)
    async def ping_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔔 You will be pinged when the run starts!",
            ephemeral=True
        )


async def start_run_flow(user):
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)

    dm = await user.create_dm()

    if len(queue) >= MAX_PLAYERS:
        await dm.send(f"❌ The queue is full! Max players: {MAX_PLAYERS}")
        return

    # Ask toon
    await dm.send("🎮 What toon do you want to be?")
    toon_msg = await bot.wait_for("message", check=check)
    toon = toon_msg.content

    # Ask HF
    await dm.send(f"📊 What is your HF? (Requirement: {HF_REQUIREMENT})")
    hf_msg = await bot.wait_for("message", check=check)

    try:
        hf = int(hf_msg.content)
    except:
        await dm.send("❌ Invalid HF number.")
        return

    if hf < HF_REQUIREMENT:
        await dm.send(f"❌ You need HF {HF_REQUIREMENT}.")
        return

    # Ask proof
    await dm.send("📸 Send proof of your HF.")
    proof_msg = await bot.wait_for("message", check=check)

    if not proof_msg.attachments:
        await dm.send("❌ No proof sent.")
        return

    # Check if already in queue
    for p in queue:
        if p["user"].id == user.id:
            await dm.send("❌ You are already in the queue!")
            return

    # Add to queue
    queue.append({
        "user": user,
        "toon": toon,
        "hf": hf
    })

    embed = discord.Embed(title="✅ Added to Queue", color=discord.Color.green())
    embed.add_field(name="Toon", value=toon)
    embed.add_field(name="HF", value=str(hf))
    embed.add_field(name="Position", value=str(len(queue)))
    embed.add_field(name="Host", value=f"{HOST_USERNAME} ({HOST_DISPLAY})")

    await dm.send(embed=embed, view=RunView())


# Player command to join queue
@bot.command()
async def run(ctx):
    await ctx.send("📩 Check your DMs!")
    await start_run_flow(ctx.author)


# View queue
@bot.command()
async def queue(ctx):
    if not queue:
        await ctx.send("❌ Queue is empty.")
        return

    embed = discord.Embed(title="📋 Current Queue", color=discord.Color.blue())
    for i, player in enumerate(queue, start=1):
        embed.add_field(
            name=f"{i}. {player['user'].name}",
            value=f"Toon: {player['toon']} | HF: {player['hf']}",
            inline=False
        )

    await ctx.send(embed=embed)


# Start run & ping everyone
@bot.command()
async def start(ctx):
    if not queue:
        await ctx.send("❌ No players in queue.")
        return

    mentions = " ".join([player["user"].mention for player in queue])

    await ctx.send(f"🚨 RUN STARTING!\n{mentions}")

    for player in queue:
        try:
            dm = await player["user"].create_dm()
            await dm.send(f"🚨 Run is starting!\n🔗 Join: {PRIVATE_SERVER_LINK}")
        except:
            pass

    queue.clear()


bot.run(os.getenv("TOKEN"))
