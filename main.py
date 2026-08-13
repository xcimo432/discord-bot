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

MOD_ROLES = [
    'Модератор',
    'Администратор'
]

ROLE_FUN = 1493930437452759101
ROLE_ADMIN = 1493930203410464849

VOICE_CREATE_ID = None

DATA = {'warns': {}, 'afk': {}}
ROOMS = {}

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

def has_role(member, role_id):
    try:
        return any(r.id == role_id for r in member.roles)
    except Exception:
        return False

def member_access(member):
    return is_allowed(member.id) or has_role(member, ROLE_FUN) or has_role(member, ROLE_ADMIN)

def mod_access(member):
    if is_allowed(member.id) or has_role(member, ROLE_ADMIN):
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

def get_own_room(member):
    try:
        ch = member.voice.channel if member.voice else None
        if ch and ch.id in ROOMS and ROOMS[ch.id]['owner'] == member.id:
            return ch
    except Exception:
        pass
    return None

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

@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if VOICE_CREATE_ID and after.channel and after.channel.id == VOICE_CREATE_ID:
            if member.bot:
                return
            if before.channel and before.channel.id == VOICE_CREATE_ID:
                return
            room = await member.guild.create_voice_channel(
                name=f'🎧 Комната • {member.display_name}',
                category=after.channel.category,
                user_limit=5
            )
            await room.set_permissions(member.guild.default_role, view_channel=False, connect=False)
            await room.set_permissions(member, view_channel=True, connect=True)
            await member.move_to(room)
            ROOMS[room.id] = {'owner': member.id}

        if before.channel and before.channel.id in ROOMS:
            room = before.channel
            if member.id == ROOMS[room.id]['owner'] or len(room.members) == 0:
                await room.delete()
                del ROOMS[room.id]
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка комнаты: {e}')

# ===== АДМИН (/) =====

@bot.tree.command(name='say', description='Отправить сообщение от лица бота')
@app_commands.describe(message='Текст сообщения')
async def say_slash(interaction: discord.Interaction, message: str):
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    await interaction.response.send_message(message)

@bot.tree.command(name='say_embed', description='Отправить красивое Embed-сообщение')
@app_commands.describe(title='Заголовок', description='Описание')
async def say_embed_slash(interaction: discord.Interaction, title: str, description: str):
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
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
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
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
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    try:
        await user.send(message)
        await interaction.response.send_message(f'✅ Отправлено {user.mention}', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)

@bot.tree.command(name='add_user', description='Добавить пользователя в список админов')
@app_commands.describe(user_id='ID пользователя')
async def add_user_slash(interaction: discord.Interaction, user_id: str):
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    uid = int(user_id)
    if uid not in ALLOWED_USERS:
        ALLOWED_USERS.append(uid)
        await interaction.response.send_message(f'✅ <@{uid}> добавлен', ephemeral=True)
    else:
        await interaction.response.send_message('❌ Уже в списке', ephemeral=True)

@bot.tree.command(name='remove_user', description='Удалить пользователя из списка админов')
@app_commands.describe(user_id='ID пользователя')
async def remove_user_slash(interaction: discord.Interaction, user_id: str):
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    uid = int(user_id)
    if uid in ALLOWED_USERS:
        ALLOWED_USERS.remove(uid)
        await interaction.response.send_message(f'✅ <@{uid}> удалён', ephemeral=True)
    else:
        await interaction.response.send_message('❌ Не в списке', ephemeral=True)

@bot.tree.command(name='list_users', description='Список админов')
async def list_users_slash(interaction: discord.Interaction):
    if not (is_allowed(interaction.user.id) or has_role(interaction.user, ROLE_ADMIN)):
        await interaction.response.send_message('❌ У тебя нет доступа!', ephemeral=True)
        return
    mentions = [f'<@{uid}>' for uid in ALLOWED_USERS]
    await interaction.response.send_message('📋 Разрешённые:\n' + '\n'.join(mentions), ephemeral=True)

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

# ===== РАЗВЛЕЧЕНИЯ (/) =====

@bot.tree.command(name='roll', description='Случайное число')
@app_commands.describe(maximum='Максимум (по умолчанию 100)')
async def roll_slash(interaction: discord.Interaction, maximum: int = 100):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    if maximum < 1:
        maximum = 1
    await interaction.response.send_message(f'🎲 **{random.randint(1, maximum)}** (от 1 до {maximum})')

@bot.tree.command(name='coin', description='Подбросить монетку')
async def coin_slash(interaction: discord.Interaction):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    result = random.choice(['🦅 Орёл', '🪙 Решка'])
    await interaction.response.send_message(result)

@bot.tree.command(name='8ball', description='Магический шар')
@app_commands.describe(question='Вопрос')
async def ball8_slash(interaction: discord.Interaction, question: str):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    answers = [
        '🎱 Да', '🎱 Нет', '🎱 Возможно', '🎱 Точно нет', '🎱 Определённо да',
        '🎱 Скорее всего', '🎱 Спроси позже', '🎱 Не думаю', '🎱 Может быть',
        '🎱 Конечно', '🎱 Вряд ли', '🎱 Только ты знаешь'
    ]
    await interaction.response.send_message(f'**{question}**\n{random.choice(answers)}')

@bot.tree.command(name='choose', description='Выбрать из вариантов')
@app_commands.describe(options='Варианты через запятую')
async def choose_slash(interaction: discord.Interaction, options: str):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    parts = [o.strip() for o in options.split(',') if o.strip()]
    if not parts:
        await interaction.response.send_message('❌ Пусто. Пример: /choose пицца, суши, бургер', ephemeral=True)
        return
    await interaction.response.send_message(f'🤔 Я выбираю: **{random.choice(parts)}**')

@bot.tree.command(name='timer', description='Таймер')
@app_commands.describe(seconds='Секунды', text='Что напомнить')
async def timer_slash(interaction: discord.Interaction, seconds: int, text: str = 'Таймер сработал'):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    if seconds < 1:
        seconds = 1
    await interaction.response.defer()
    await asyncio.sleep(seconds)
    await interaction.followup.send(f'⏰ {interaction.user.mention}, время вышло! **{text}**')

@bot.tree.command(name='afk', description='Уйти в AFK')
@app_commands.describe(reason='Причина')
async def afk_slash(interaction: discord.Interaction, reason: str = 'Не указана'):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    DATA['afk'][str(interaction.user.id)] = {
        'reason': reason,
        'time': discord.utils.utcnow().strftime('%d.%m.%Y %H:%M')
    }
    save_data()
    await interaction.response.send_message(f'💤 {interaction.user.mention}, ты ушёл в AFK. Причина: **{reason}**')

@bot.tree.command(name='joke', description='Случайная шутка')
async def joke_slash(interaction: discord.Interaction):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
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

# ===== ИНФО / ОБЩЕЕ (/) =====

@bot.tree.command(name='hello', description='Поздороваться')
async def hello_slash(interaction: discord.Interaction):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    await interaction.response.send_message(f'Привет, {interaction.user.mention}!')

@bot.tree.command(name='ping', description='Проверить задержку')
async def ping_slash(interaction: discord.Interaction):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    await interaction.response.send_message(f'🏓 Понг! {round(bot.latency * 1000)}мс')

@bot.tree.command(name='info', description='Информация о боте')
async def info_slash(interaction: discord.Interaction):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    embed = discord.Embed(
        title='ℹ️ Информация',
        description='Бот для управления сервером',
        color=discord.Color.green()
    )
    embed.add_field(name='Название', value=bot.user.name)
    embed.add_field(name='ID', value=bot.user.id)
    embed.add_field(name='Разрешённых', value=len(ALLOWED_USERS))
    embed.add_field(name='Префикс', value='/')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='avatar', description='Показать аватар')
@app_commands.describe(user='Пользователь')
async def avatar_slash(interaction: discord.Interaction, user: discord.Member = None):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    user = user or interaction.user
    embed = discord.Embed(title=f'🖼️ Аватар — {user.display_name}', color=discord.Color.blue())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='userinfo', description='Информация об участнике')
@app_commands.describe(user='Пользователь')
async def userinfo_slash(interaction: discord.Interaction, user: discord.Member = None):
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
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
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
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
    if not member_access(interaction.user):
        await interaction.response.send_message('❌ Нет доступа!', ephemeral=True)
        return
    if not interaction.guild.icon:
        await interaction.response.send_message('❌ У сервера нет иконки', ephemeral=True)
        return
    embed = discord.Embed(title=f'🖼️ Иконка — {interaction.guild.name}', color=discord.Color.blue())
    embed.set_image(url=interaction.guild.icon.url)
    await interaction.response.send_message(embed=embed)

# ===== ГОЛОСОВЫЕ КОМНАТЫ (/) =====

@bot.tree.command(name='vlimit', description='Лимит участников комнаты')
@app_commands.describe(limit='Максимум участников')
async def vlimit_slash(interaction: discord.Interaction, limit: int):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.edit(user_limit=limit)
    await interaction.response.send_message(f'🔵 Лимит комнаты: **{limit}**')

@bot.tree.command(name='vclose', description='Закрыть вход в комнату')
async def vclose_slash(interaction: discord.Interaction):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(interaction.guild.default_role, connect=False)
    await interaction.response.send_message('🟠 Вход в комнату закрыт')

@bot.tree.command(name='vopen', description='Открыть вход в комнату')
async def vopen_slash(interaction: discord.Interaction):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(interaction.guild.default_role, connect=True)
    await interaction.response.send_message('🟡 Вход в комнату открыт')

@bot.tree.command(name='vdeny', description='Забрать доступ к комнате')
@app_commands.describe(user='Участник')
async def vdeny_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(user, connect=False)
    await user.move_to(None)
    await interaction.response.send_message(f'🔴 {user.mention} больше не может войти')

@bot.tree.command(name='vallow', description='Выдать доступ к комнате')
@app_commands.describe(user='Участник')
async def vallow_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(user, connect=True)
    await interaction.response.send_message(f'✅ {user.mention} может войти в комнату')

@bot.tree.command(name='vrename', description='Переименовать комнату')
@app_commands.describe(name='Новое имя')
async def vrename_slash(interaction: discord.Interaction, name: str):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.edit(name=f'🎧 {name}')
    await interaction.response.send_message(f'✏️ Комната переименована в **{name}**')

@bot.tree.command(name='vtransfer', description='Передать владельца комнаты')
@app_commands.describe(user='Новый владелец')
async def vtransfer_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    ROOMS[room.id]['owner'] = user.id
    await room.set_permissions(user, view_channel=True, connect=True)
    await interaction.response.send_message(f'👑 Владелец комнаты теперь {user.mention}')

@bot.tree.command(name='vkick', description='Выгнать из комнаты')
@app_commands.describe(user='Участник')
async def vkick_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await user.move_to(None)
    await interaction.response.send_message(f'⚪ {user.mention} выгнан из комнаты')

@bot.tree.command(name='vmute', description='Отключить микрофон')
@app_commands.describe(user='Участник')
async def vmute_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await user.edit(mute=True)
    await interaction.response.send_message(f'📢 {user.mention} замьючен')

@bot.tree.command(name='vunmute', description='Включить микрофон')
@app_commands.describe(user='Участник')
async def vunmute_slash(interaction: discord.Interaction, user: discord.Member):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await user.edit(mute=False)
    await interaction.response.send_message(f'🔊 {user.mention} размьючен')

@bot.tree.command(name='vhide', description='Скрыть комнату из списка')
async def vhide_slash(interaction: discord.Interaction):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(interaction.guild.default_role, view_channel=False)
    await interaction.response.send_message('👁 Комната скрыта из списка')

@bot.tree.command(name='vunhide', description='Показать комнату в списке')
async def vunhide_slash(interaction: discord.Interaction):
    room = get_own_room(interaction.user)
    if not room:
        await interaction.response.send_message('❌ Ты не владелец комнаты', ephemeral=True)
        return
    await room.set_permissions(interaction.guild.default_role, view_channel=True)
    await interaction.response.send_message('👁 Комната снова видна в списке')

# ===== HELP =====

@bot.tree.command(name='help', description='Список всех команд')
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title='📖 Команды бота',
        description='Доступ зависят от роли:\n🔹 Роль «Развлечения/Общее» — инфо и развлечения\n🔹 Роль «Админ» — всё',
        color=discord.Color.blue()
    )
    embed.add_field(name='📝 Админ', value='/say • /say_embed • /say_rule • /say_dm • /add_user • /remove_user • /list_users', inline=False)
    embed.add_field(name='🛡️ Модерация', value='/kick • /ban • /unban • /timeout • /untimeout • /warn • /warns • /warn_clear • /lock • /unlock • /slowmode • /nick • /clear', inline=False)
    embed.add_field(name='ℹ️ Инфо', value='/info • /avatar • /userinfo • /serverinfo • /servericon', inline=False)
    embed.add_field(name='🎲 Развлечения', value='/roll • /coin • /8ball • /choose • /timer • /afk • /joke', inline=False)
    embed.add_field(name='🔧 Общее', value='/hello • /ping • /help', inline=False)
    embed.add_field(name='🎮 Управление комнатой', value='(только владелец, из своего голосового канала)\n/vlimit — лимит участников\n/vclose — закрыть вход\n/vopen — открыть вход\n/vdeny — забрать доступ\n/vallow — выдать доступ\n/vrename — переименовать\n/vtransfer — передать владельца\n/vkick — выгнать из комнаты\n/vmute — отключить микрофон\n/vunmute — включить микрофон\n/vhide — скрыть из списка\n/vunhide — показать в списке', inline=False)
    await interaction.response.send_message(embed=embed)

if __name__ == '__main__':
    load_data()
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print('[A.A.I.-01] ОШИБКА: Неверный токен!')
    except Exception as e:
        print(f'[A.A.I.-01] Ошибка: {e}')