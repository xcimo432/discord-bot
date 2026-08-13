import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '/'

ALLOWED_USERS = [
    796346440213200906,
    646241782983819294
]

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

def is_allowed(user_id):
    return user_id in ALLOWED_USERS

@bot.event
async def on_ready():
    print(f'[A.A.I.-01] Бот запущен как {bot.user.name}')
    print(f'[A.A.I.-01] ID бота: {bot.user.id}')
    print(f'[A.A.I.-01] Разрешённые пользователи: {ALLOWED_USERS}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Flowmusic'))
    
    try:
        synced = await bot.tree.sync()
        print(f'[A.A.I.-01] Слеш-команд синхронизировано: {len(synced)}')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка синхронизации: {e}')

# ===== СЛЕШ-КОМАНДЫ =====

@bot.tree.command(name='say', description='Отправить сообщение от лица бота')
@app_commands.describe(message='Текст сообщения')
async def say(interaction: discord.Interaction, message: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа к этой команде!', ephemeral=True)
        return
    await interaction.response.send_message(message)

@bot.tree.command(name='say_embed', description='Отправить красивое Embed-сообщение')
@app_commands.describe(title='Заголовок', description='Описание')
async def say_embed(interaction: discord.Interaction, title: str, description: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа к этой команде!', ephemeral=True)
        return
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='say_rule', description='Отправить правило в красивом оформлении')
@app_commands.describe(
    title='Заголовок правила',
    color='Цвет (red, green, blue, yellow, purple, orange, black, gray, white)',
    description='Текст правила'
)
async def say_rule(interaction: discord.Interaction, title: str, color: str, description: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа к этой команде!', ephemeral=True)
        return
    
    colors = {
        'red': discord.Color.red(),
        'green': discord.Color.green(),
        'blue': discord.Color.blue(),
        'yellow': discord.Color.yellow(),
        'purple': discord.Color.purple(),
        'orange': discord.Color.orange(),
        'black': discord.Color.dark_gray(),
        'gray': discord.Color.greyple(),
        'white': discord.Color.light_gray()
    }
    embed_color = colors.get(color.lower(), discord.Color.blue())
    
    embed = discord.Embed(
        title=f'📌 {title}',
        description=description,
        color=embed_color
    )
    embed.set_footer(text=f'{interaction.user.display_name}', icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='say_dm', description='Отправить сообщение в ЛС от лица бота')
@app_commands.describe(user='Пользователь', message='Текст сообщения')
async def say_dm(interaction: discord.Interaction, user: discord.User, message: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа к этой команде!', ephemeral=True)
        return
    try:
        await user.send(message)
        await interaction.response.send_message(f'✅ Сообщение отправлено пользователю {user.mention}', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)

@bot.tree.command(name='add_user', description='Добавить пользователя в список разрешённых')
@app_commands.describe(user_id='ID пользователя')
async def add_user(interaction: discord.Interaction, user_id: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    try:
        uid = int(user_id)
        if uid not in ALLOWED_USERS:
            ALLOWED_USERS.append(uid)
            await interaction.response.send_message(f'✅ Пользователь <@{uid}> добавлен в список разрешённых', ephemeral=True)
        else:
            await interaction.response.send_message('❌ Этот пользователь уже в списке', ephemeral=True)
    except ValueError:
        await interaction.response.send_message('❌ Введи корректный ID пользователя', ephemeral=True)

@bot.tree.command(name='remove_user', description='Удалить пользователя из списка разрешённых')
@app_commands.describe(user_id='ID пользователя')
async def remove_user(interaction: discord.Interaction, user_id: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    try:
        uid = int(user_id)
        if uid in ALLOWED_USERS:
            ALLOWED_USERS.remove(uid)
            await interaction.response.send_message(f'✅ Пользователь <@{uid}> удалён из списка разрешённых', ephemeral=True)
        else:
            await interaction.response.send_message('❌ Этот пользователь не в списке', ephemeral=True)
    except ValueError:
        await interaction.response.send_message('❌ Введи корректный ID пользователя', ephemeral=True)

@bot.tree.command(name='list_users', description='Показать список разрешённых пользователей')
async def list_users(interaction: discord.Interaction):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    mentions = [f'<@{uid}>' for uid in ALLOWED_USERS]
    await interaction.response.send_message(f'📋 Разрешённые пользователи:\n' + '\n'.join(mentions), ephemeral=True)

@bot.tree.command(name='hello', description='Поздороваться с ботом')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Привет, {interaction.user.mention}!')

@bot.tree.command(name='ping', description='Проверить задержку бота')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Понг! Задержка: {round(bot.latency * 1000)}мс')

@bot.tree.command(name='commands', description='Показать список всех команд')
async def commands_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title='📋 Список команд бота',
        description='Все команды бота.',
        color=discord.Color.blue()
    )
    embed.add_field(name='/say [текст]', value='Отправить сообщение от лица бота', inline=False)
    embed.add_field(name='/say_embed [заголовок] [описание]', value='Отправить красивое Embed-сообщение', inline=False)
    embed.add_field(name='/say_rule [заголовок] [цвет] [описание]', value='Отправить правило с цветом\nЦвета: red, green, blue, yellow, purple, orange, black, gray, white', inline=False)
    embed.add_field(name='/say_dm [@пользователь] [текст]', value='Отправить сообщение в ЛС', inline=False)
    embed.add_field(name='/add_user [ID]', value='Добавить пользователя', inline=False)
    embed.add_field(name='/remove_user [ID]', value='Удалить пользователя', inline=False)
    embed.add_field(name='/list_users', value='Список разрешённых', inline=False)
    embed.add_field(name='/hello', value='Поздороваться', inline=False)
    embed.add_field(name='/ping', value='Проверить задержку', inline=False)
    embed.add_field(name='/commands', value='Показать этот список', inline=False)
    embed.set_footer(text='✅ - требуют прав доступа | 🟢 - доступны всем')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='clear', description='Очистить сообщения в канале')
@app_commands.describe(amount='Количество сообщений (макс. 100)')
async def clear(interaction: discord.Interaction, amount: int = 5):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа к этой команде!', ephemeral=True)
        return
    if amount > 100:
        amount = 100
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f'🗑️ Удалено {len(deleted)} сообщений', ephemeral=True)

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')
