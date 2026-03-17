import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

HF_REQUIREMENT = 24
HOST_USERNAME = "TheRealGreen129"
HOST_DISPLAY = "green"
PRIVATE_SERVER_LINK = "PUT_YOUR_PRIVATE_SERVER_LINK_HERE"

class RunView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Private Server", style=discord.ButtonStyle.green)
    async def join_server(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Join here: {PRIVATE_SERVER_LINK}",
            ephemeral=True
        )

    @discord.ui.button(label="Ping Me When Starting", style=discord.ButtonStyle.blurple)
    async def ping_me(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "You'll be pinged when the run starts!",
            ephemeral=True
        )

async def start_run_flow(user):
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)

    dm = await user.create_dm()

    await dm.send("🎮 What toon do you want to be?")
    toon_msg = await bot.wait_for("message", check=check)
    toon = toon_msg.content

    await dm.send(f"📊 What is your HF? (Requirement: {HF_REQUIREMENT})")
    hf_msg = await bot.wait_for("message", check=check)

    try:
        hf = int(hf_msg.content)
    except:
        await dm.send("❌ Invalid HF.")
        return

    if hf < HF_REQUIREMENT:
        await dm.send(f"❌ You need HF {HF_REQUIREMENT}.")
        return

    await dm.send("📸 Send proof of your HF.")
    proof_msg = await bot.wait_for("message", check=check)

    if not proof_msg.attachments:
        await dm.send("❌ No proof sent.")
        return

    embed = discord.Embed(title="✅ Accepted", color=discord.Color.green())
    embed.add_field(name="Toon", value=toon)
    embed.add_field(name="HF", value=str(hf))
    embed.add_field(name="Host", value=f"{HOST_USERNAME} ({HOST_DISPLAY})")

    await dm.send(embed=embed, view=RunView())

@bot.command()
async def run(ctx):
    await ctx.send("📩 Check DMs!")
    await start_run_flow(ctx.author)

bot.run(os.getenv("TOKEN"))
