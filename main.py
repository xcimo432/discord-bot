import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '!'

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

# ===== СЛЕШ-КОМАНДЫ (/) =====

@bot.tree.command(name='say', description='Отправить сообщение от лица бота')
@app_commands.describe(message='Текст сообщения')
async def say_slash(interaction: discord.Interaction, message: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await interaction.response.send_message(message)

@bot.tree.command(name='say_embed', description='Отправить красивое Embed-сообщение')
@app_commands.describe(title='Заголовок', description='Описание')
async def say_embed_slash(interaction: discord.Interaction, title: str, description: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='say_rule', description='Отправить правило в красивом оформлении')
@app_commands.describe(
    title='Заголовок правила',
    color='Цвет (red, green, blue, yellow, purple, orange, black, gray, white)',
    description='Текст правила'
)
async def say_rule_slash(interaction: discord.Interaction, title: str, color: str, description: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
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
    embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='say_dm', description='Отправить сообщение в ЛС от лица бота')
@app_commands.describe(user='Пользователь', message='Текст сообщения')
async def say_dm_slash(interaction: discord.Interaction, user: discord.User, message: str):
    if not is_allowed(interaction.user.id):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    try:
        await user.send(message)
        await interaction.response.send_message(f'✅ Отправлено {user.mention}', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)

@bot.tree.command(name='hello', description='Поздороваться')
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'Привет, {interaction.user.mention}!')

@bot.tree.command(name='ping', description='Проверить задержку')
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Понг! {round(bot.latency * 1000)}мс')

@bot.tree.command(name='commands', description='Показать список команд')
async def commands_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title='📋 Список команд бота',
        description='Работают и с `!` и с `/`',
        color=discord.Color.blue()
    )
    embed.add_field(name='/say', value='Отправить сообщение', inline=False)
    embed.add_field(name='/say_embed', value='Красивое сообщение', inline=False)
    embed.add_field(name='/say_rule', value='Правило с цветом', inline=False)
    embed.add_field(name='/say_dm', value='Сообщение в ЛС', inline=False)
    embed.add_field(name='/hello', value='Поздороваться', inline=False)
    embed.add_field(name='/ping', value='Задержка', inline=False)
    embed.add_field(name='/commands', value='Этот список', inline=False)
    await interaction.response.send_message(embed=embed)

# ===== КОМАНДЫ С ! (ДУБЛИРУЮТ) =====

@bot.command(name='say')
async def say_prefix(ctx, *, message):
    if not is_allowed(ctx.author.id):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name='say_embed')
async def say_embed_prefix(ctx, title, *, description):
    if not is_allowed(ctx.author.id):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.message.delete()
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name='say_rule')
async def say_rule_prefix(ctx, title, color: str = 'blue', *, description):
    if not is_allowed(ctx.author.id):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.message.delete()
    
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
    embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@bot.command(name='say_dm')
async def say_dm_prefix(ctx, user: discord.User, *, message):
    if not is_allowed(ctx.author.id):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    try:
        await user.send(message)
        await ctx.reply(f'✅ Отправлено {user.mention}', delete_after=3)
    except Exception as e:
        await ctx.reply(f'❌ Ошибка: {e}', delete_after=3)

@bot.command(name='hello')
async def hello_prefix(ctx):
    await ctx.reply(f'Привет, {ctx.author.mention}!')

@bot.command(name='ping')
async def ping_prefix(ctx):
    await ctx.reply(f'🏓 Понг! {round(bot.latency * 1000)}мс')

@bot.command(name='commands')
async def commands_prefix(ctx):
    embed = discord.Embed(
        title='📋 Список команд бота',
        description='Работают и с `!` и с `/`',
        color=discord.Color.blue()
    )
    embed.add_field(name='!say', value='Отправить сообщение', inline=False)
    embed.add_field(name='!say_embed', value='Красивое сообщение', inline=False)
    embed.add_field(name='!say_rule', value='Правило с цветом', inline=False)
    embed.add_field(name='!say_dm', value='Сообщение в ЛС', inline=False)
    embed.add_field(name='!hello', value='Поздороваться', inline=False)
    embed.add_field(name='!ping', value='Задержка', inline=False)
    embed.add_field(name='!commands', value='Этот список', inline=False)
    await ctx.reply(embed=embed)

@bot.command(name='add_user')
async def add_user(ctx, user_id: int):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    if user_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(user_id)
        await ctx.reply(f'✅ <@{user_id}> добавлен')
    else:
        await ctx.reply('❌ Уже в списке')

@bot.command(name='remove_user')
async def remove_user(ctx, user_id: int):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    if user_id in ALLOWED_USERS:
        ALLOWED_USERS.remove(user_id)
        await ctx.reply(f'✅ <@{user_id}> удалён')
    else:
        await ctx.reply('❌ Не в списке')

@bot.command(name='list_users')
async def list_users(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    mentions = [f'<@{uid}>' for uid in ALLOWED_USERS]
    await ctx.reply('📋 Разрешённые:\n' + '\n'.join(mentions))

@bot.command(name='clear')
async def clear(ctx, amount: int = 5):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Удалено {len(deleted) - 1}', delete_after=3)

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(
        title='ℹ️ Информация',
        description='Бот для управления сервером',
        color=discord.Color.green()
    )
    embed.add_field(name='Название', value=bot.user.name)
    embed.add_field(name='ID', value=bot.user.id)
    embed.add_field(name='Разрешённых', value=len(ALLOWED_USERS))
    embed.add_field(name='Префикс', value='! и /')
    await ctx.reply(embed=embed)

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')