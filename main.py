import discord
from discord.ext import commands
import os

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '!'

ALLOWED_USERS = [
    796346440213200906,
    646241782983819294
]

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

def is_allowed(ctx):
    return ctx.author.id in ALLOWED_USERS

@bot.event
async def on_ready():
    print(f'[A.A.I.-01] Бот запущен как {bot.user.name}')
    print(f'[A.A.I.-01] ID бота: {bot.user.id}')
    print(f'[A.A.I.-01] Разрешённые пользователи: {ALLOWED_USERS}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Flowmusic'))

# ===== КОМАНДЫ =====

@bot.command(name='commands')
async def commands_command(ctx):
    """Показать все команды бота"""
    embed = discord.Embed(
        title='📋 Список команд бота',
        description='Все команды бота. Команды с ✅ доступны только разрешённым пользователям.',
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name='✅ !say [текст]',
        value='Отправить сообщение от лица бота',
        inline=False
    )
    embed.add_field(
        name='✅ !say_embed [заголовок] [описание]',
        value='Отправить красивое Embed-сообщение',
        inline=False
    )
    embed.add_field(
        name='✅ !say_rule [заголовок] [цвет] [описание]',
        value='Отправить правило в красивом оформлении\nЦвета: red, green, blue, yellow, purple, orange, black, gray, white',
        inline=False
    )
    embed.add_field(
        name='✅ !say_dm [@пользователь] [текст]',
        value='Отправить сообщение в ЛС от лица бота',
        inline=False
    )
    embed.add_field(
        name='✅ !add_user [ID]',
        value='Добавить пользователя в список разрешённых',
        inline=False
    )
    embed.add_field(
        name='✅ !remove_user [ID]',
        value='Удалить пользователя из списка разрешённых',
        inline=False
    )
    embed.add_field(
        name='✅ !list_users',
        value='Показать список разрешённых пользователей',
        inline=False
    )
    embed.add_field(
        name='✅ !clear [кол-во]',
        value='Очистить сообщения в канале (макс. 100)',
        inline=False
    )
    embed.add_field(
        name='🟢 !hello',
        value='Бот поздоровается с тобой',
        inline=False
    )
    embed.add_field(
        name='🟢 !ping',
        value='Проверить задержку бота',
        inline=False
    )
    embed.add_field(
        name='🟢 !info',
        value='Показать информацию о боте',
        inline=False
    )
    embed.add_field(
        name='🟢 !commands',
        value='Показать этот список команд',
        inline=False
    )
    
    embed.set_footer(text='✅ - требуют прав доступа | 🟢 - доступны всем')
    await ctx.reply(embed=embed)

@bot.command(name='say')
async def say(ctx, *, message):
    if not is_allowed(ctx):
        await ctx.reply('❌ У тебя нет доступа к этой команде!', delete_after=3)
        return
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name='say_embed')
async def say_embed(ctx, title, *, description):
    if not is_allowed(ctx):
        await ctx.reply('❌ У тебя нет доступа к этой команде!', delete_after=3)
        return
    await ctx.message.delete()
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name='say_rule')
async def say_rule(ctx, title, color: str = 'blue', *, description):
    if not is_allowed(ctx):
        await ctx.reply('❌ У тебя нет доступа к этой команде!', delete_after=3)
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
    embed.set_footer(text=f'{ctx.author.display_name}', icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@bot.command(name='say_dm')
async def say_dm(ctx, user: discord.User, *, message):
    if not is_allowed(ctx):
        await ctx.reply('❌ У тебя нет доступа к этой команде!', delete_after=3)
        return
    try:
        await user.send(message)
        await ctx.reply(f'✅ Сообщение отправлено пользователю {user.mention}', delete_after=3)
    except Exception as e:
        await ctx.reply(f'❌ Ошибка: {e}', delete_after=3)

@bot.command(name='add_user')
async def add_user(ctx, user_id: int):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ У тебя нет доступа!', delete_after=3)
        return
    if user_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(user_id)
        await ctx.reply(f'✅ Пользователь <@{user_id}> добавлен в список разрешённых')
    else:
        await ctx.reply('❌ Этот пользователь уже в списке')

@bot.command(name='remove_user')
async def remove_user(ctx, user_id: int):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ У тебя нет доступа!', delete_after=3)
        return
    if user_id in ALLOWED_USERS:
        ALLOWED_USERS.remove(user_id)
        await ctx.reply(f'✅ Пользователь <@{user_id}> удалён из списка разрешённых')
    else:
        await ctx.reply('❌ Этот пользователь не в списке')

@bot.command(name='list_users')
async def list_users(ctx):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ У тебя нет доступа!', delete_after=3)
        return
    mentions = [f'<@{uid}>' for uid in ALLOWED_USERS]
    await ctx.reply(f'📋 Разрешённые пользователи:\n' + '\n'.join(mentions))

@bot.command(name='clear')
async def clear(ctx, amount: int = 5):
    if ctx.author.id not in ALLOWED_USERS:
        await ctx.reply('❌ У тебя нет доступа к этой команде!', delete_after=3)
        return
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Удалено {len(deleted) - 1} сообщений', delete_after=3)

@bot.command(name='hello')
async def hello(ctx):
    await ctx.reply(f'Привет, {ctx.author.mention}!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.reply(f'🏓 Понг! Задержка: {round(bot.latency * 1000)}мс')

@bot.command(name='info')
async def info(ctx):
    embed = discord.Embed(
        title='ℹ️ Информация о боте',
        description='Бот создан для управления сервером',
        color=discord.Color.green()
    )
    embed.add_field(name='Название', value=bot.user.name)
    embed.add_field(name='ID', value=bot.user.id)
    embed.add_field(name='Разрешённых пользователей', value=len(ALLOWED_USERS))
    embed.add_field(name='Префикс', value=PREFIX)
    embed.set_footer(text='A.A.I.-01')
    await ctx.reply(embed=embed)

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')
