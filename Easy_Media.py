# -*- coding: utf-8 -*-

import argparse
import json
import datetime
import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_headers import Headers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from discord.ext import commands, tasks
from selenium.webdriver.common.by import By
import discord
import chromedriver_autoinstaller

# Configuration du bot Discord
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Initialisation des variables globales
tiktok_associations = {}

# Charger les associations TikTok à partir du fichier
with open('tiktoks_name.txt', 'r') as tiktok_file:
    lines = tiktok_file.readlines()
    for line in lines:
        parts = line.strip().split(' - ')
        if len(parts) == 3:
            user_id, username, _ = parts
            tiktok_associations[int(user_id)] = username

# Fonction de journalisation des commandes
def log_command(command):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('log.txt', 'a') as log_file:
        log_file.write(f"{timestamp} - {command}\n")

# Variable pour stocker le leaderboard
leaderboard = None

# Événement déclenché lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')
    await update_leaderboard(force=False)


# Fonction pour mettre à jour le leaderboard
async def update_leaderboard(force=False):
    global tiktok_associations
    channel_id = 1234567891234567890
    channel = bot.get_channel(channel_id)

    if channel:
        try:
            await clear_bot_messages(channel)
            await build_leaderboard(channel)
        except Exception as e:
            print(f"An error occurred in update_leaderboard: {str(e)}")


# Événement déclenché lorsqu'une réaction est ajoutée
@bot.event
async def on_reaction_add(reaction, user):
    global tiktok_associations
    global leaderboard

    if user.bot:  # Ignorer les réactions du bot lui-même
        return

    # Vérifier si la réaction a eu lieu dans le canal leaderboard
    channel_id = 1187747963720712282
    if reaction.message.channel.id == channel_id:
        # Réagir à l'emoji ➕
        if reaction.emoji == "➕":
            await reaction.remove(user)
            # Envoyer un message pour demander le pseudo TikTok
            prompt_message = await reaction.message.channel.send(f"{user.mention}, veuillez entrer votre pseudo TikTok en réponse à ce message.")

            try:
                # Attendre la réponse de l'utilisateur pendant 60 secondes
                response = await bot.wait_for("message", check=lambda m: m.author == user, timeout=60.0)

                # Supprimer le message de demande du pseudo
                await prompt_message.delete()

                # Afficher la barre de chargement
                loading_message = await reaction.message.channel.send(f"{user.mention}, traitement en cours... 🟩")
                for _ in range(1):
                    await asyncio.sleep(1)
                    await loading_message.edit(content=f"{user.mention}, 🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩🟩🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩🟩🟩🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, 🟩🟩🟩🟩🟩🟩🟩")
                    await asyncio.sleep(0.5)
                    await loading_message.edit(content=f"{user.mention}, ✅✅✅✅✅✅✅")

                # Utiliser la réponse pour ajouter le TikTok
                username = response.content
                log_command(f"{user.name} ({user.id}) a exécuté la commande $addtiktok {username}")

                if user.id in tiktok_associations:
                    print(f"{user.mention}, vous êtes déjà dans le leaderboard.")

                tiktok_associations[user.id] = username
                followers_count = await get_tiktok_followers_count(username)

                with open('tiktoks_name.txt', 'a') as tiktok_file:
                    tiktok_file.write(f"{user.id} - {username} - {followers_count}\n")

                message = await reaction.message.channel.send(f'{user.mention} a ajouté son TikTok : {username} avec {followers_count} abonnés')
                await asyncio.sleep(3)

                # Supprimer les messages
                await message.delete()
                await response.delete()
                await loading_message.delete()
                await update_leaderboard(force=True)

            except asyncio.TimeoutError:
                await reaction.message.channel.send(f"{user.mention}, la demande a expiré. Veuillez réessayer.")
                # Supprimer le message de demande du pseudo
                await prompt_message.delete()

        # Réagir à l'emoji ➖
        elif reaction.emoji == "➖":
            await reaction.remove(user)
            if user.id in tiktok_associations:
                with open('tiktoks_name.txt', 'r') as tiktok_file:
                    lines = tiktok_file.readlines()

                with open('tiktoks_name.txt', 'w') as tiktok_file:
                    for line in lines:
                        parts = line.strip().split(' - ')
                        if len(parts) == 3 and int(parts[0]) != user.id:
                            tiktok_file.write(line)

                del tiktok_associations[user.id]
                message = await reaction.message.channel.send(f'{user.mention}, votre TikTok a été retiré du leaderboard.')
                await asyncio.sleep(2.5)  # Attendre 2.5 secondes
                await reaction.message.delete()
                await message.delete()
                await update_leaderboard(force=True)
            else:
                await reaction.message.channel.send(f'{user.mention}, vous ne faites pas partie du leaderboard.')
                await asyncio.sleep(3)
                await reaction.delete()

        elif reaction.emoji == "👀":
            await reaction.remove(user)
            if user.id in tiktok_associations:
                with open('tiktoks_name.txt', 'r') as tiktok_file:
                    lines = tiktok_file.readlines()
                    # Obtenir le classement du user dans le fichier tiktoks_name.txt
                    user_id = user.id
                    user_rank = get_user_rank(user_id)

                    # Envoyer un message avec le classement
                    message = await reaction.message.channel.send(f"{user.mention}, Vous êtes classé(e) {user_rank}e.")
                    await asyncio.sleep(5)  # Attendre 5 secondes
                    await message.delete()
            else:
                await reaction.message.channel.send(f'{user.mention}, vous ne faites pas partie du leaderboard.')
                await asyncio.sleep(3)
                await reaction.delete()


# Fonction pour obtenir le classement d'un utilisateur
def get_user_rank(user_id):
    with open('tiktoks_name.txt', 'r') as tiktok_file:
        lines = tiktok_file.readlines()
        sorted_data = sorted(lines, key=lambda x: int(x.strip().split(' - ')[2]), reverse=True)

    for rank, line in enumerate(sorted_data, start=1):
        parts = line.strip().split(' - ')
        if len(parts) == 3 and int(parts[0]) == user_id:
            return rank

    return None


# Fonction pour obtenir le nombre d'abonnés TikTok
async def get_tiktok_followers_count(username):
    # Configuration des options du pilote Chrome
    options = webdriver.ChromeOptions()
    options.binary_location = '/python/chrome-linux64/chrome'
    options.add_argument('--headless')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Création de l'instance du pilote Chrome
    driver = webdriver.Chrome(options=options)
    
    try:
        tiktok_url = f'https://www.tiktok.com/@{username}'

        driver.get(tiktok_url)

        driver.implicitly_wait(5)

        followers_count_element = driver.find_element(By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[1]/h3/div[2]/strong')

        followers_count_text = followers_count_element.text

        return followers_count_text

    except Exception as e:
        return f"Erreur lors de l'execution : {str(e)}"

    finally:
        driver.quit()


# Fonction pour construire le leaderboard
@bot.event
async def build_leaderboard(channel, force=False):
    tiktok_data = []
    with open('tiktoks_name.txt', 'r') as tiktok_file:
        lines = tiktok_file.readlines()
        for line in lines:
            parts = line.strip().split(' - ')
            if len(parts) == 3:
                user_id, username, followers_count = parts
                if followers_count.lower() != 'none':
                    tiktok_data.append({'user_id': int(user_id), 'username': username, 'followers_count': int(followers_count)})

    sorted_data = sorted(tiktok_data, key=lambda x: x['followers_count'], reverse=True)

    embed = discord.Embed(
        title="TikTok Followers Leaderboard",
        description="Classement des membres par followers TikTok.",
        color=0xffffff
    )

    for rank, member_data in enumerate(sorted_data, start=1):
        member_id = member_data['user_id']
        username = member_data['username']
        followers_count = member_data['followers_count']
        member = bot.get_user(member_id)
        if member:
            embed.add_field(
                name=f"#{rank} - {followers_count} followers",
                value=f"<@{member_id}> - TikTok: {username}",
                inline=False
            )

    if force:
        if leaderboard:
            await leaderboard.delete()

        leaderboard = await channel.send(embed=embed)

        # Ajouter les réactions
        await leaderboard.add_reaction("➕")  # Emoji +
        await leaderboard.add_reaction("➖")  # Emoji -
        await leaderboard.add_reaction("👀")  # Emoji 👀

    else:
        leaderboard = await channel.send(embed=embed)
        # Ajouter les réactions
        await leaderboard.add_reaction("➕")  # Emoji +
        await leaderboard.add_reaction("➖")  # Emoji -
        await leaderboard.add_reaction("👀")  # Emoji 👀


# Fonction pour effacer les messages du bot dans un canal
async def clear_bot_messages(channel):
    async for message in channel.history(limit=None):
        if message.author == bot.user:
            await message.delete()


# Événement déclenché lorsqu'un message est reçu
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignorer les messages du bot lui-même

    # Vérifier si le message commence par le préfixe
    if message.content.startswith('$'):
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)  # Ajoutez cette ligne pour traiter les événements de réaction


# Événement déclenché lorsqu'un message est modifié
@bot.event
async def on_message_edit(before, after):
    await bot.process_commands(after)

# Lancer le bot avec le token approprié
bot.run('TOKEN')
