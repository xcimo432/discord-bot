import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import asyncio
import re
from datetime import timedelta

TOKEN = os.environ.get('DISCORD_TOKEN')
PREFIX = '!'
DATA_FILE = 'data.json'

ALLOWED_USERS = [
    796346440213200906,
    646241782983819294
]

DATA = {'warns': {}, 'afk': {}}

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

def load_data():
    global DATA
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            DATA = json.load(f)
    except Exception:
        DATA = {'warns': {}, 'afk': {}}
    if 'warns' not in DATA:
        DATA['warns'] = {}
    if 'afk' not in DATA:
        DATA['afk'] = {}

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)

def is_allowed(user_id):
    return user_id in ALLOWED_USERS

def mod_access(member):
    if is_allowed(member.id):
        return True
    try:
        if member.guild_permissions.administrator or member.guild_permissions.manage_messages or member.guild_permissions.manage_guild:
            return True
    except Exception:
        pass
    return False

def parse_duration(text):
    total = 0
    for m in re.finditer(r'(\d+)\s*([smhd])', text.lower()):
        num = int(m.group(1))
        total += num * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[m.group(2)]
    return total or None

COLORS = {
    'red': discord.Color.red(),
    'green': discord.Color.green(),
    'blue': discord.Color.blue(),
    'yellow': discord.Color.yellow(),
    'purple': discord.Color.purple(),
    'orange': discord.Color.orange(),
    'black': discord.Color.from_rgb(31, 31, 31),
    'gray': discord.Color.greyple(),
    'white': discord.Color.light_gray()
}

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

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_data()

    if str(message.author.id) in data.get('afk', {}):
        del data['afk'][str(message.author.id)]
        save_data()
        await message.channel.send(f'👋 {message.author.mention}, убрал твой AFK!')

    for m in message.mentions:
        if str(m.id) in data.get('afk', {}):
            info = data['afk'][str(m.id)]
            await message.reply(f'💤 {m.mention} сейчас AFK: **{info["reason"]}**')

    await bot.process_commands(message)

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

    embed_color = COLORS.get(color.lower(), discord.Color.blue())

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

# ===== МОДЕРАЦИЯ (/) =====

@bot.tree.command(name='kick', description='Выгнать участника')
@app_commands.describe(user='Участник', reason='Причина')
async def kick_slash(interaction: discord.Interaction, user: discord.Member, reason: str = 'Не указана'):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await user.kick(reason=reason)
    await interaction.response.send_message(f'👢 {user.mention} выгнан. Причина: **{reason}**')

@bot.tree.command(name='ban', description='Забанить участника')
@app_commands.describe(user='Участник', reason='Причина')
async def ban_slash(interaction: discord.Interaction, user: discord.Member, reason: str = 'Не указана'):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await user.ban(reason=reason)
    await interaction.response.send_message(f'🔨 {user.mention} забанен. Причина: **{reason}**')

@bot.tree.command(name='unban', description='Разбанить по ID')
@app_commands.describe(user_id='ID пользователя')
async def unban_slash(interaction: discord.Interaction, user_id: str):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f'✅ {user.name} разбанен')
    except Exception as e:
        await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)

@bot.tree.command(name='timeout', description='Заткнуть участника (мьют)')
@app_commands.describe(user='Участник', duration='Длительность: 10m, 1h, 1d', reason='Причина')
async def timeout_slash(interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = 'Не указана'):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    sec = parse_duration(duration)
    if not sec:
        await interaction.response.send_message('❌ Неверный формат. Пример: 10m, 1h, 1d', ephemeral=True)
        return
    sec = min(sec, 2419200)
    await user.timeout(discord.utils.utcnow() + timedelta(seconds=sec), reason=reason)
    await interaction.response.send_message(f'🔇 {user.mention} замьючен на **{duration}**. Причина: **{reason}**')

@bot.tree.command(name='untimeout', description='Снять мьют')
@app_commands.describe(user='Участник')
async def untimeout_slash(interaction: discord.Interaction, user: discord.Member):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await user.timeout(None, reason='Снят мьют')
    await interaction.response.send_message(f'🔊 {user.mention} снова может говорить')

@bot.tree.command(name='warn', description='Выдать предупреждение')
@app_commands.describe(user='Участник', reason='Причина')
async def warn_slash(interaction: discord.Interaction, user: discord.Member, reason: str = 'Не указана'):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    uid = str(user.id)
    if uid not in DATA['warns']:
        DATA['warns'][uid] = []
    DATA['warns'][uid].append({'reason': reason, 'by': str(interaction.user), 'time': discord.utils.utcnow().strftime('%d.%m.%Y %H:%M')})
    save_data()
    await interaction.response.send_message(f'⚠️ {user.mention} получил предупреждение. Причина: **{reason}** (всего: {len(DATA["warns"][uid])})')

@bot.tree.command(name='warns', description='Список предупреждений')
@app_commands.describe(user='Участник')
async def warns_slash(interaction: discord.Interaction, user: discord.Member):
    uid = str(user.id)
    warns = DATA['warns'].get(uid, [])
    if not warns:
        await interaction.response.send_message(f'✅ У {user.mention} нет предупреждений', ephemeral=True)
        return
    embed = discord.Embed(title=f'⚠️ Предупреждения — {user.display_name}', color=discord.Color.orange())
    for i, w in enumerate(warns, 1):
        embed.add_field(name=f'#{i}', value=f'**{w["reason"]}**\nОт: {w["by"]} • {w["time"]}', inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='warn_clear', description='Очистить предупреждения')
@app_commands.describe(user='Участник')
async def warn_clear_slash(interaction: discord.Interaction, user: discord.Member):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    DATA['warns'][str(user.id)] = []
    save_data()
    await interaction.response.send_message(f'✅ Предупреждения {user.mention} очищены')

@bot.tree.command(name='lock', description='Закрыть канал')
async def lock_slash(interaction: discord.Interaction):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message(f'🔒 Канал {interaction.channel.mention} закрыт')

@bot.tree.command(name='unlock', description='Открыть канал')
async def unlock_slash(interaction: discord.Interaction):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
    await interaction.response.send_message(f'🔓 Канал {interaction.channel.mention} открыт')

@bot.tree.command(name='slowmode', description='Установить слоумод')
@app_commands.describe(seconds='Секунды (0 = выключить)')
async def slowmode_slash(interaction: discord.Interaction, seconds: int):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f'🐌 Слоумод канала: **{seconds} сек**')

@bot.tree.command(name='nick', description='Сменить ник участника')
@app_commands.describe(user='Участник', name='Новый ник')
async def nick_slash(interaction: discord.Interaction, user: discord.Member, name: str):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await user.edit(nick=name)
    await interaction.response.send_message(f'✏️ Ник {user.mention} изменён на **{name}**')

@bot.tree.command(name='clear', description='Очистить сообщения')
@app_commands.describe(amount='Количество (макс. 100)')
async def clear_slash(interaction: discord.Interaction, amount: int = 5):
    if not mod_access(interaction.user):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    if amount > 100:
        amount = 100
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f'🗑️ Удалено {amount}', ephemeral=True)

# ===== ИНФО / ФАН (/) =====

@bot.tree.command(name='hello', description='Поздороваться')
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'Привет, {interaction.user.mention}!')

@bot.tree.command(name='ping', description='Проверить задержку')
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'🏓 Понг! {round(bot.latency * 1000)}мс')

@bot.tree.command(name='info', description='Информация о боте')
async def info_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title='ℹ️ Информация',
        description='Бот для управления сервером',
        color=discord.Color.green()
    )
    embed.add_field(name='Название', value=bot.user.name)
    embed.add_field(name='ID', value=bot.user.id)
    embed.add_field(name='Разрешённых', value=len(ALLOWED_USERS))
    embed.add_field(name='Префикс', value='! и /')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='avatar', description='Показать аватар')
@app_commands.describe(user='Пользователь')
async def avatar_slash(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f'🖼️ Аватар — {user.display_name}', color=discord.Color.blue())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo', description='Информация об участнике')
@app_commands.describe(user='Пользователь')
async def userinfo_slash(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f'👤 {user.display_name}', color=user.color if user.color.value else discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name='Никнейм', value=user.name)
    embed.add_field(name='ID', value=user.id)
    embed.add_field(name='Статус', value=str(user.status).replace('dnd', 'не беспокоить').replace('online', 'в сети').replace('idle', 'отошёл').replace('offline', 'не в сети'))
    embed.add_field(name='Аккаунт создан', value=user.created_at.strftime('%d.%m.%Y'))
    embed.add_field(name='Присоединился', value=user.joined_at.strftime('%d.%m.%Y') if user.joined_at else '—')
    embed.add_field(name='Топ-роль', value=user.top_role.mention if user.top_role else '—')
    embed.add_field(name='Роли', value=f'{len(user.roles) - 1}')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='serverinfo', description='Информация о сервере')
async def serverinfo_slash(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f'ℹ️ {guild.name}', color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name='👑 Владелец', value=guild.owner.mention if guild.owner else '—')
    embed.add_field(name='👥 Участники', value=guild.member_count)
    embed.add_field(name='💬 Каналы', value=f'{len(guild.text_channels)} текст / {len(guild.voice_channels)} голос')
    embed.add_field(name='🎭 Роли', value=len(guild.roles))
    embed.add_field(name='📅 Создан', value=guild.created_at.strftime('%d.%m.%Y'))
    embed.add_field(name='ID', value=guild.id)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='servericon', description='Показать иконку сервера')
async def servericon_slash(interaction: discord.Interaction):
    if not interaction.guild.icon:
        await interaction.response.send_message('❌ У сервера нет иконки', ephemeral=True)
        return
    embed = discord.Embed(title=f'🖼️ Иконка — {interaction.guild.name}', color=discord.Color.blue())
    embed.set_image(url=interaction.guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='roll', description='Случайное число')
@app_commands.describe(maximum='Максимум (по умолчанию 100)')
async def roll_slash(interaction: discord.Interaction, maximum: int = 100):
    if maximum < 1:
        maximum = 1
    await interaction.response.send_message(f'🎲 **{random.randint(1, maximum)}** (от 1 до {maximum})')

@bot.tree.command(name='coin', description='Подбросить монетку')
async def coin_slash(interaction: discord.Interaction):
    result = random.choice(['🦅 Орёл', '🪙 Решка'])
    await interaction.response.send_message(result)

@bot.tree.command(name='8ball', description='Магический шар')
@app_commands.describe(question='Вопрос')
async def ball8_slash(interaction: discord.Interaction, question: str):
    answers = [
        '🎱 Да', '🎱 Нет', '🎱 Возможно', '🎱 Точно нет', '🎱 Определённо да',
        '🎱 Скорее всего', '🎱 Спроси позже', '🎱 Не думаю', '🎱 Может быть',
        '🎱 Конечно', '🎱 Вряд ли', '🎱 Только ты знаешь'
    ]
    await interaction.response.send_message(f'**{question}**\n{random.choice(answers)}')

@bot.tree.command(name='choose', description='Выбрать из вариантов')
@app_commands.describe(options='Варианты через запятую')
async def choose_slash(interaction: discord.Interaction, options: str):
    parts = [o.strip() for o in options.split(',') if o.strip()]
    if not parts:
        await interaction.response.send_message('❌ Пусто. Пример: /choose пицца, суши, бургер', ephemeral=True)
        return
    await interaction.response.send_message(f'🤔 Я выбираю: **{random.choice(parts)}**')

@bot.tree.command(name='timer', description='Таймер')
@app_commands.describe(seconds='Секунды', text='Что напомнить')
async def timer_slash(interaction: discord.Interaction, seconds: int, text: str = 'Таймер сработал'):
    if seconds < 1:
        seconds = 1
    await interaction.response.defer()
    await asyncio.sleep(seconds)
    await interaction.followup.send(f'⏰ {interaction.user.mention}, время вышло! **{text}**')

@bot.tree.command(name='afk', description='Уйти в AFK')
@app_commands.describe(reason='Причина')
async def afk_slash(interaction: discord.Interaction, reason: str = 'Не указана'):
    DATA['afk'][str(interaction.user.id)] = {
        'reason': reason,
        'time': discord.utils.utcnow().strftime('%d.%m.%Y %H:%M')
    }
    save_data()
    await interaction.response.send_message(f'💤 {interaction.user.mention}, ты ушёл в AFK. Причина: **{reason}**')

@bot.tree.command(name='joke', description='Случайная шутка')
async def joke_slash(interaction: discord.Interaction):
    jokes = [
        'Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 == DEC 25.',
        '— У меня есть баг в коде. — А я думал, это фича, которая вышла из-под контроля.',
        'Что сказал один байт другому? — Ты слишком 0 или слишком 1, соберись!',
        'Идут два программиста. Один говорит: «Хорошая погода». Второй: «Да, но дождь мог бы быть поумнее».',
        'Сколько программистов нужно, чтобы поменять лампочку? Ни одного — это проблема железа.',
        '99 багов в коде, 99 багов. Исправь один — и вот 99 багов в коде снова... потому что было 100.',
        'Программист — это машина для превращения кофе в код.',
        '— Доктор, у меня в памяти утечка. — Запустите garbage collector и приходите через неделю.'
    ]
    await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name='help', description='Список всех команд')
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title='📋 Все команды бота',
        description='Работают и с `!` и с `/`',
        color=discord.Color.blue()
    )
    embed.add_field(name='📝 Админ', value='/say • /say_embed • /say_rule • /say_dm', inline=False)
    embed.add_field(name='🛡️ Модерация', value='/kick • /ban • /unban • /timeout • /untimeout • /warn • /warns • /warn_clear • /lock • /unlock • /slowmode • /nick • /clear', inline=False)
    embed.add_field(name='ℹ️ Инфо', value='/info • /avatar • /userinfo • /serverinfo • /servericon', inline=False)
    embed.add_field(name='🎲 Развлечения', value='/roll • /coin • /8ball • /choose • /timer • /afk • /joke', inline=False)
    embed.add_field(name='🔧 Общее', value='/hello • /ping • /help', inline=False)
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

    embed_color = COLORS.get(color.lower(), discord.Color.blue())

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

# ===== МОДЕРАЦИЯ (!) =====

@bot.command(name='kick')
async def kick_prefix(ctx, user: discord.Member, *, reason='Не указана'):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await user.kick(reason=reason)
    await ctx.send(f'👢 {user.mention} выгнан. Причина: **{reason}**')

@bot.command(name='ban')
async def ban_prefix(ctx, user: discord.Member, *, reason='Не указана'):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await user.ban(reason=reason)
    await ctx.send(f'🔨 {user.mention} забанен. Причина: **{reason}**')

@bot.command(name='unban')
async def unban_prefix(ctx, user_id: int):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'✅ {user.name} разбанен')
    except Exception as e:
        await ctx.reply(f'❌ Ошибка: {e}', delete_after=3)

@bot.command(name='timeout')
async def timeout_prefix(ctx, user: discord.Member, duration='10m', *, reason='Не указана'):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    sec = parse_duration(duration)
    if not sec:
        await ctx.reply('❌ Неверный формат. Пример: 10m, 1h, 1d', delete_after=5)
        return
    sec = min(sec, 2419200)
    await user.timeout(discord.utils.utcnow() + timedelta(seconds=sec), reason=reason)
    await ctx.send(f'🔇 {user.mention} замьючен на **{duration}**. Причина: **{reason}**')

@bot.command(name='untimeout')
async def untimeout_prefix(ctx, user: discord.Member):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await user.timeout(None, reason='Снят мьют')
    await ctx.send(f'🔊 {user.mention} снова может говорить')

@bot.command(name='warn')
async def warn_prefix(ctx, user: discord.Member, *, reason='Не указана'):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    uid = str(user.id)
    if uid not in DATA['warns']:
        DATA['warns'][uid] = []
    DATA['warns'][uid].append({'reason': reason, 'by': str(ctx.author), 'time': ctx.message.created_at.strftime('%d.%m.%Y %H:%M')})
    save_data()
    await ctx.send(f'⚠️ {user.mention} получил предупреждение. Причина: **{reason}** (всего: {len(DATA["warns"][uid])})')

@bot.command(name='warns')
async def warns_prefix(ctx, user: discord.Member = None):
    user = user or ctx.author
    warns = DATA['warns'].get(str(user.id), [])
    if not warns:
        await ctx.reply(f'✅ У {user.mention} нет предупреждений')
        return
    embed = discord.Embed(title=f'⚠️ Предупреждения — {user.display_name}', color=discord.Color.orange())
    for i, w in enumerate(warns, 1):
        embed.add_field(name=f'#{i}', value=f'**{w["reason"]}**\nОт: {w["by"]} • {w["time"]}', inline=False)
    await ctx.send(embed=embed)

@bot.command(name='warn_clear')
async def warn_clear_prefix(ctx, user: discord.Member):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    DATA['warns'][str(user.id)] = []
    save_data()
    await ctx.send(f'✅ Предупреждения {user.mention} очищены')

@bot.command(name='lock')
async def lock_prefix(ctx):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f'🔒 Канал {ctx.channel.mention} закрыт')

@bot.command(name='unlock')
async def unlock_prefix(ctx):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send(f'🔓 Канал {ctx.channel.mention} открыт')

@bot.command(name='slowmode')
async def slowmode_prefix(ctx, seconds: int = 0):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f'🐌 Слоумод канала: **{seconds} сек**')

@bot.command(name='nick')
async def nick_prefix(ctx, user: discord.Member, *, name):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    await user.edit(nick=name)
    await ctx.send(f'✏️ Ник {user.mention} изменён на **{name}**')

@bot.command(name='clear')
async def clear_prefix(ctx, amount: int = 5):
    if not mod_access(ctx.author):
        await ctx.reply('❌ Нет доступа!', delete_after=3)
        return
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Удалено {len(deleted) - 1}', delete_after=3)

# ===== ИНФО / ФАН (!) =====

@bot.command(name='hello')
async def hello_prefix(ctx):
    await ctx.reply(f'Привет, {ctx.author.mention}!')

@bot.command(name='ping')
async def ping_prefix(ctx):
    await ctx.reply(f'🏓 Понг! {round(bot.latency * 1000)}мс')

@bot.command(name='info')
async def info_prefix(ctx):
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

@bot.command(name='avatar')
async def avatar_prefix(ctx, user: discord.Member = None):
    user = user or ctx.author
    embed = discord.Embed(title=f'🖼️ Аватар — {user.display_name}', color=discord.Color.blue())
    embed.set_image(url=user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='userinfo')
async def userinfo_prefix(ctx, user: discord.Member = None):
    user = user or ctx.author
    embed = discord.Embed(title=f'👤 {user.display_name}', color=user.color if user.color.value else discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name='Никнейм', value=user.name)
    embed.add_field(name='ID', value=user.id)
    embed.add_field(name='Статус', value=str(user.status).replace('dnd', 'не беспокоить').replace('online', 'в сети').replace('idle', 'отошёл').replace('offline', 'не в сети'))
    embed.add_field(name='Аккаунт создан', value=user.created_at.strftime('%d.%m.%Y'))
    embed.add_field(name='Присоединился', value=user.joined_at.strftime('%d.%m.%Y') if user.joined_at else '—')
    embed.add_field(name='Топ-роль', value=user.top_role.mention if user.top_role else '—')
    embed.add_field(name='Роли', value=f'{len(user.roles) - 1}')
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo_prefix(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f'ℹ️ {guild.name}', color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name='👑 Владелец', value=guild.owner.mention if guild.owner else '—')
    embed.add_field(name='👥 Участники', value=guild.member_count)
    embed.add_field(name='💬 Каналы', value=f'{len(guild.text_channels)} текст / {len(guild.voice_channels)} голос')
    embed.add_field(name='🎭 Роли', value=len(guild.roles))
    embed.add_field(name='📅 Создан', value=guild.created_at.strftime('%d.%m.%Y'))
    embed.add_field(name='ID', value=guild.id)
    await ctx.send(embed=embed)

@bot.command(name='servericon')
async def servericon_prefix(ctx):
    if not ctx.guild.icon:
        await ctx.reply('❌ У сервера нет иконки')
        return
    embed = discord.Embed(title=f'🖼️ Иконка — {ctx.guild.name}', color=discord.Color.blue())
    embed.set_image(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command(name='roll')
async def roll_prefix(ctx, maximum: int = 100):
    if maximum < 1:
        maximum = 1
    await ctx.send(f'🎲 **{random.randint(1, maximum)}** (от 1 до {maximum})')

@bot.command(name='coin')
async def coin_prefix(ctx):
    result = random.choice(['🦅 Орёл', '🪙 Решка'])
    await ctx.send(result)

@bot.command(name='8ball')
async def ball8_prefix(ctx, *, question):
    answers = [
        '🎱 Да', '🎱 Нет', '🎱 Возможно', '🎱 Точно нет', '🎱 Определённо да',
        '🎱 Скорее всего', '🎱 Спроси позже', '🎱 Не думаю', '🎱 Может быть',
        '🎱 Конечно', '🎱 Вряд ли', '🎱 Только ты знаешь'
    ]
    await ctx.send(f'**{question}**\n{random.choice(answers)}')

@bot.command(name='choose')
async def choose_prefix(ctx, *, options):
    parts = [o.strip() for o in options.split(',') if o.strip()]
    if not parts:
        await ctx.reply('❌ Пусто. Пример: !choose пицца, суши, бургер')
        return
    await ctx.send(f'🤔 Я выбираю: **{random.choice(parts)}**')

@bot.command(name='timer')
async def timer_prefix(ctx, seconds: int, *, text='Таймер сработал'):
    if seconds < 1:
        seconds = 1
    await ctx.send(f'⏰ Таймер на **{seconds} сек** запущен!')
    await asyncio.sleep(seconds)
    await ctx.send(f'⏰ {ctx.author.mention}, время вышло! **{text}**')

@bot.command(name='afk')
async def afk_prefix(ctx, *, reason='Не указана'):
    DATA['afk'][str(ctx.author.id)] = {
        'reason': reason,
        'time': ctx.message.created_at.strftime('%d.%m.%Y %H:%M')
    }
    save_data()
    await ctx.send(f'💤 {ctx.author.mention}, ты ушёл в AFK. Причина: **{reason}**')

@bot.command(name='joke')
async def joke_prefix(ctx):
    jokes = [
        'Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 == DEC 25.',
        '— У меня есть баг в коде. — А я думал, это фича, которая вышла из-под контроля.',
        'Что сказал один байт другому? — Ты слишком 0 или слишком 1, соберись!',
        'Идут два программиста. Один говорит: «Хорошая погода». Второй: «Да, но дождь мог бы быть поумнее».',
        'Сколько программистов нужно, чтобы поменять лампочку? Ни одного — это проблема железа.',
        '99 багов в коде, 99 багов. Исправь один — и вот 99 багов в коде снова... потому что было 100.',
        'Программист — это машина для превращения кофе в код.',
        '— Доктор, у меня в памяти утечка. — Запустите garbage collector и приходите через неделю.'
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name='help')
async def help_prefix(ctx):
    embed = discord.Embed(
        title='📋 Все команды бота',
        description='Работают и с `!` и с `/`',
        color=discord.Color.blue()
    )
    embed.add_field(name='📝 Админ', value='!say • !say_embed • !say_rule • !say_dm • !add_user • !remove_user • !list_users', inline=False)
    embed.add_field(name='🛡️ Модерация', value='!kick • !ban • !unban • !timeout • !untimeout • !warn • !warns • !warn_clear • !lock • !unlock • !slowmode • !nick • !clear', inline=False)
    embed.add_field(name='ℹ️ Инфо', value='!info • !avatar • !userinfo • !serverinfo • !servericon', inline=False)
    embed.add_field(name='🎲 Развлечения', value='!roll • !coin • !8ball • !choose • !timer • !afk • !joke', inline=False)
    embed.add_field(name='🔧 Общее', value='!hello • !ping • !help', inline=False)
    await ctx.send(embed=embed)

# ===== АДМИН-КОМАНДЫ (!) =====

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'❌ Не хватает аргумента: `{error.param.name}`. Напиши `!help`', delete_after=5)
    elif isinstance(error, commands.MemberNotFound):
        await ctx.reply('❌ Участник не найден', delete_after=5)
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.reply(f'❌ Ошибка: {error}', delete_after=5)

if __name__ == '__main__':
    load_data()
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')