import os
import discord
import requests
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name="scan",
    description="Verifica configurações básicas de segurança"
)
async def scan(interaction: discord.Interaction, url: str):

    await interaction.response.defer()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        headers = {
            key.lower(): value
            for key, value in response.headers.items()
        }

        resultado = []

        resultado.append(
            f"🌐 Status HTTP: `{response.status_code}`"
        )

        if response.url.startswith("https://"):
            resultado.append("🔒 HTTPS: ✅")
        else:
            resultado.append("🔒 HTTPS: ❌")

        verificacoes = {
            "strict-transport-security": "HSTS",
            "content-security-policy": "Content-Security-Policy",
            "x-content-type-options": "X-Content-Type-Options",
            "x-frame-options": "X-Frame-Options",
            "referrer-policy": "Referrer-Policy"
        }

        resultado.append("\n**Headers de segurança:**")

        for header, nome in verificacoes.items():
            if header in headers:
                resultado.append(f"✅ {nome}")
            else:
                resultado.append(f"⚠️ {nome} não encontrado")

        embed = discord.Embed(
            title="🔎 Relatório básico",
            description="\n".join(resultado),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="URL final",
            value=response.url[:1024],
            inline=False
        )

        await interaction.followup.send(embed=embed)

    except requests.exceptions.SSLError:
        await interaction.followup.send(
            "🔐 Não foi possível validar o certificado HTTPS."
        )

    except requests.exceptions.RequestException:
        await interaction.followup.send(
            "❌ Não consegui acessar esse endereço."
        )


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot conectado como {client.user}")


client.run(TOKEN)