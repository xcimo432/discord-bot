import discord
from discord.ext import commands
import os

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '/'

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
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Готов к работе'))

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
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Удалено {len(deleted) - 1} сообщений', delete_after=3)

@bot.command(name='hello')
async def hello(ctx):
    await ctx.reply(f'Привет, {ctx.author.mention}!')

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')
