import discord, config, requests, datetime, wikipedia, pymysql
from discord import utils
from discord.ext import commands
from bs4 import BeautifulSoup
from random import randint

bot = commands.Bot(command_prefix='~', intents=discord.Intents.all(), help_command=None)

@bot.event
async def on_ready():
    try:
        global creator
        global date
        global yesterday
        creator = await bot.fetch_user(318720256795344896)
        date = datetime.datetime.today()
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        print(f'We have logged as {bot.user}')
        config.botstatus = '✅'
        wikipedia.set_lang("ru")
        try:
            connection = await connectsql()
            config.sqlstatus = '✅'
        except:
            print('SQL error')
    except:
        print('Fatal error')

@bot.event
async def on_member_join(member):
    try:
        connection = await connectsql()
        user = str(member.name) + '#' + str(member.discriminator)
        role = utils.get(member.guild.roles, id=config.ROLE)
        emb = discord.Embed(title=f"У нас новый гражданский! {user}", value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)
        await member.add_roles(role)
        print('Подключился к серверу и получил роль', user)
        emb = discord.Embed(title='Досье:', value='\u200b', color=0x008000)
        emb.add_field(name=f"Имя:", value=member.name, inline=True)
        emb.add_field(name=f"Идентификатор:", value=member.discriminator, inline=True)
        emb.set_thumbnail(url=member.avatar_url)
        emb.add_field(name=f"ID:", value=member.id, inline=False)
        emb.add_field(name=f"Статус:", value=member.status, inline=True)
        if member.activities == ():
            emb.add_field(name=f"Активность:", value='отсутствует', inline=True)
        else:
            emb.add_field(name=f"Активность:", value=member.activities, inline=True)
        roles = member.roles
        rowRoles = ''
        for i in roles:
            rowRoles = rowRoles + str(i) + ' '
        emb.add_field(name=f"Роли:", value=rowRoles, inline=False)
        emb.add_field(name=f"Дата:", value=member.joined_at.strftime("%d-%m-%Y %H:%M:%S"), inline=False)
        emb.set_author(name=f"Досье составил: {bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)
        with connection:
            cur = connection.cursor()
            insert_query = "SELECT * FROM blacklist"
            cur.execute(insert_query)
            rows = cur.fetchall()
            if rows != ():
                for i in rows:
                    if i['login'] == user:
                        emb = discord.Embed(title=f'{user} обнаружен в black hole этого сервера. Будет уничтожен!',
                                            value='\u200b', color=0xff0000)
                        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                        await bot.get_channel(config.CHANNEL).send(embed=emb)
                        await member.kick(reason=f'black hole')
                        break
    except:
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)

@bot.event
async def on_member_remove(member):
    try:
        user = str(member.name) + '#' + str(member.discriminator)
        emb = discord.Embed(title=f"{user} покинул нас", value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)
    except:
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)

@bot.event
async def on_message(message):
    try:
        connection = await connectsql()
        author = message.author.name + '#' + message.author.discriminator
        with connection:
            cur = connection.cursor()
            insert_query = "SELECT * FROM mute"
            cur.execute(insert_query)
            rows = cur.fetchall()
            if rows != ():
                for i in rows:
                    if i['login'] == author:
                        await message.delete()
                        break
        await bot.process_commands(message)
    except:
        await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, exception):
    message = await ctx.fetch_message(ctx.message.id)
    message_text = message.content.partition(' ')
    await message.delete()
    print(f'Ошибка выполнения команды.', type(exception), exception)
    if isinstance(exception, discord.ext.commands.errors.MissingRequiredArgument):
        emb = discord.Embed(title=f'{ctx.message.author.nick}, неверный синтаксис команды {message_text[0]}', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb, delete_after = 3)
        return
    if isinstance(exception, discord.ext.commands.errors.CommandNotFound):
        emb = discord.Embed(title=f'{ctx.message.author.nick}, команда {message_text[0]} не найдена, используй ~help', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb, delete_after = 3)
        return
    emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
    emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
    emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
    await bot.get_channel(config.CHANNEL).send(embed=emb, delete_after = 3)

@bot.command(pass_context=True)
async def blackhole(ctx):
    try:
        connection = await connectsql()
        with connection:
            cur = connection.cursor()
            insert_query = "SELECT * FROM blacklist"
            cur.execute(insert_query)
            rows = cur.fetchall()
            if rows != ():
                emb = discord.Embed(title=f"Наш общий black hole:", value='\u200b', color=0xff0000)
                emb.add_field(name=f'Всего записей: {len(rows)}', value='\u200b', inline=False)
                count = 1
                for i in rows:
                    a = i['login']
                    emb.add_field(name=f'{count}. {a}', value='\u200b', inline=False)
                    count += 1
                emb.set_author(name=f"Black hole охраняет: {bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(title=f"Милорд, наш black hole пуст", value='\u200b', color=0xff0000)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def admins(ctx):
    try:
        connection = await connectsql()
        with connection:
            cur = connection.cursor()
            insert_query = "SELECT * FROM admins"
            cur.execute(insert_query)
            rows = cur.fetchall()
            if rows != ():
                emb = discord.Embed(title=f"Admins:", value='\u200b', color=0xff0000)
                emb.add_field(name=f'Всего записей: {len(rows)}', value='\u200b', inline=False)
                count = 1
                for i in rows:
                    a = i['login']
                    emb.add_field(name=f'{count}. {a}', value='\u200b', inline=False)
                    count += 1
                emb.set_author(name=f"Список предоставил: {bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(title=f"Пусто..", value='\u200b', color=0xff0000)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def addadmin(ctx, *, arg):
    try:
        if ctx.message.author.id == 318720256795344896:
            connection = await connectsql()
            with connection.cursor() as cursor:
                cur = connection.cursor()
                insert_query = "SELECT * FROM admins"
                cur.execute(insert_query)
                rows = cur.fetchall()
                if rows != ():
                    for i in rows:
                        a = i['login']
                        if a == arg:
                            emb = discord.Embed(title=f'Уже админ ._.', value='\u200b',
                                                color=0xff0000)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
                            return
                insert_query = f"INSERT INTO admins (login) VALUES ('{arg}');"
                cursor.execute(insert_query)
                connection.commit()
                emb = discord.Embed(title=f'{arg} успешно добавлен в admins', value='\u200b', color=0x00FF00)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
        else:
            emb = discord.Embed(title='Ошибка', value='\u200b', color=0x008000)
            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
            emb.add_field(name=f"Недостаточно прав", value='\u200b', inline=False)
            await ctx.channel.send(embed=emb)
    except:
        pass

@bot.command(pass_context=True)
async def deleteadmin(ctx, *, arg):
    try:
        if ctx.message.author.id == 318720256795344896:
            connection = await connectsql()
            with connection.cursor() as cursor:
                insert_query = f"SELECT * FROM admins"
                cursor.execute(insert_query)
                rows = cursor.fetchall()
                if rows != ():
                    arg = str(arg)
                    for i in rows:
                        user = i['login']
                        if user == arg:
                            insert_query = f"DELETE FROM admins WHERE login = ('{arg}');"
                            cursor.execute(insert_query)
                            connection.commit()
                            emb = discord.Embed(title=f'{arg} успешно удален из admins', value='\u200b',
                                                color=0x00FF00)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
                        else:
                            emb = discord.Embed(title=f'Данный пользователь не найден в admins', value='\u200b',
                                                color=0xff0000)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
                else:
                    emb = discord.Embed(title=f"Там уже пусто!", value='\u200b', color=0xff0000)
                    emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                    emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                    await ctx.channel.send(embed=emb)
        else:
            emb = discord.Embed(title='Ошибка', value='\u200b', color=0x008000)
            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
            emb.add_field(name=f"Недостаточно прав", value='\u200b', inline=False)
            await ctx.channel.send(embed=emb)
    except:
        pass

@bot.command(pass_context=True)
async def status(ctx):
    try:
        emb = discord.Embed(title='Status', value='\u200b', color=0x00FBF0)
        emb.add_field(name=f"Bot: {config.botstatus}", value='\u200b', inline=False)
        emb.add_field(name=f"SQL server: {config.sqlstatus}", value='\u200b', inline=False)
        emb.add_field(name=f"Ping: {bot.latency} ms", value='\u200b', inline=False)
        emb.set_author(name=f"Информацию предоставил: {bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)
        await ctx.message.delete()
    except:
        emb = discord.Embed(title=f'Fatal error, status is not working, вся информация в консоли', value='\u200b',
                            color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)
        await ctx.message.delete()

@bot.command(pass_context=True)
async def addtoblackhole(ctx, *, arg):
    try:
        connection = await connectsql()
        with connection.cursor() as cursor:
            insert_query = f"SELECT * FROM admins"
            cursor.execute(insert_query)
            rows = cursor.fetchall()
            if rows != ():
                arg = str(arg)
                for i in rows:
                    user = i['login']
                    if user == arg:
                        insert_query = f"DELETE FROM admins WHERE login = ('{arg}');"
                        cursor.execute(insert_query)
                        connection.commit()
                        emb = discord.Embed(title=f'{arg} успешно удален из admins', value='\u200b',
                                            color=0x00FF00)
                        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                        await ctx.channel.send(embed=emb)
                    else:
                        emb = discord.Embed(title=f'Данный пользователь не найден в admins', value='\u200b',
                                            color=0xff0000)
                        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                        await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(title=f"Там пусто уже", value='\u200b', color=0xff0000)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
    except:
        print('Ошибка выполнения команды addtoblackhole')
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def deletefromblackhole(ctx, *, arg):
    connection = await connectsql()
    try:
        with connection.cursor() as cursor:
            insert_query = f"SELECT * FROM blacklist"
            cursor.execute(insert_query)
            rows = cursor.fetchall()
            if rows != ():
                if arg == 'all':
                    for i in rows:
                        user = i['login']
                        insert_query = f"DELETE FROM blacklist WHERE login = ('{user}');"
                        cursor.execute(insert_query)
                        connection.commit()
                    emb = discord.Embed(title=f'Black hole был успешно очищен', value='\u200b', color=0x00FF00)
                    emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                    emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                    await ctx.channel.send(embed=emb)
                else:
                    arg = str(arg)
                    for i in rows:
                        user = i['login']
                        if user == arg:
                            insert_query = f"DELETE FROM blacklist WHERE login = ('{arg}');"
                            cursor.execute(insert_query)
                            connection.commit()
                            emb = discord.Embed(title=f'{arg} успешно удален из black hole', value='\u200b',
                                                color=0x00FF00)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
                        else:
                            emb = discord.Embed(title=f'Данный пользователь не найден в black hole', value='\u200b',
                                                color=0xff0000)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(title=f"Милорд, наш black hole пуст", value='\u200b', color=0xff0000)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
    except:
        print('Ошибка выполнения команды deletefromblackhole')
        emb = discord.Embed(title=f'Fatal error', value='\u200b', color=0xff0000)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def help(ctx):
    try:
        emb = discord.Embed(title='Команды:', value='\u200b', color=0xffff00)
        emb.add_field(name=f"~status", value='Узнать статус бота и SQL сервера', inline=False)
        emb.add_field(name=f"~blackhole", value='Заглянуть в black hole', inline=False)
        emb.add_field(name=f"~addtoblackhole (user login)", value='Добавить человека в black hole', inline=False)
        emb.add_field(name=f"~deletefromblackhole (user login or 'all')",
                      value='Удалить человека из/полностью очистить black hole', inline=False)
        emb.add_field(name=f"~info (@login)", value='Собрать самое полное досье на человека', inline=False)
        emb.add_field(name=f"~search (вопрос)", value='Задать вопрос Вассерману', inline=False)
        emb.add_field(name=f"~USD", value='Узнать курс доллара', inline=False)
        emb.add_field(name=f"~mute", value='Список пользователей с выключенным чатом', inline=False)
        emb.add_field(name=f"~muteadd (@login)", value='Выключить чат пользователю', inline=False)
        emb.add_field(name=f"~unmute (@login)", value='Включить чат пользователю', inline=False)
        emb.add_field(name=f"~EUR", value='Узнать курс евро', inline=False)
        emb.add_field(name=f"~random", value='Вассерман сделает выбор за вас (до шести вариантов)', inline=False)
        emb.set_author(name=f"Информацию предоставил: {bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title=f'Ошибка выполнения команды help', value='\u200b', color=0xff0000)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def info(ctx, *, member: discord.Member):
    try:
        emb = discord.Embed(title='Досье:', value='\u200b', color=0x008000)
        emb.add_field(name=f"Имя:", value=member.name, inline=True)
        emb.add_field(name=f"Псевдоним:", value=member.display_name, inline=True)
        emb.add_field(name=f"Идентификатор:", value=member.discriminator, inline=True)
        emb.set_thumbnail(url=member.avatar_url)
        emb.add_field(name=f"ID:", value=member.id, inline=False)
        emb.add_field(name=f"Статус:", value=member.status, inline=True)
        emb.add_field(name=f"Подробнее:", value=member.activity, inline=True)
        roles = member.roles
        rowRoles = ''
        for i in roles:
            rowRoles = rowRoles + str(i) + ' '
        emb.add_field(name=f"Роли:", value=rowRoles, inline=False)
        emb.add_field(name=f"Дата появления:", value=member.joined_at.strftime("%d-%m-%Y %H:%M:%S"), inline=True)
        emb.add_field(name=f"Дата составления досье:", value=date.strftime('%d-%m-%Y'), inline=True)
        emb.set_author(name=f"Досье составил: {bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)
    except:
        emb = discord.Embed(title='Ошибка составления', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await bot.get_channel(config.CHANNEL).send(embed=emb)

@bot.command(pass_context=True)
async def search(ctx, *, arg):
    try:
        answer = str(wikipedia.summary(f"{arg}", sentences=5))
        answer_url = str(wikipedia.page(f"{arg}").url)
        emb = discord.Embed(title='Ответ Вассермана:', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name='\u200b', value=f"{answer}", inline=False)
        emb.set_thumbnail(url=wikipedia.page(f"{arg}").images[1])
        emb.add_field(name='\u200b', value=f"{answer_url}", inline=False)
        await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title='Ответ Вассермана:', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name='\u200b', value=f"Ничего не найдено :(", inline=False)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def USD(ctx):
    try:
        text = await parser_cbr()
        emb = discord.Embed(title='Курс доллара(by cbr.ru):', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name=yesterday.strftime('%d-%m-%Y'), value=f"{text[1]}", inline=False)
        emb.add_field(name=date.strftime('%d-%m-%Y'), value=f"{text[2]}", inline=False)
        await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title='Error', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name=f"cbr.ru не отвечает", value='\u200b', inline=False)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def EUR(ctx):
    try:
        text = await parser_cbr()
        emb = discord.Embed(title='Курс евро(by cbr.ru):', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name=yesterday.strftime('%d-%m-%Y'), value=f"{text[4]}", inline=False)
        emb.add_field(name=date.strftime('%d-%m-%Y'), value=f"{text[5]}", inline=False)
        await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title='Error', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name=f"cbr.ru не отвечает", value='\u200b', inline=False)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def random(ctx, arg1, arg2, arg3=None, arg4=None, arg5=None, arg6=None):
    try:
        count = 2
        user = None
        if arg3 is not None:
            count += 1
        if arg4 is not None:
            count += 1
        if arg5 is not None:
            count += 1
        if arg6 is not None:
            count += 1
        rand = randint(1, count)
        if rand == 1:
            user = arg1
        if rand == 2:
            user = arg2
        if rand == 3:
            user = arg3
        if rand == 4:
            user = arg4
        if rand == 5:
            user = arg5
        if rand == 6:
            user = arg6
        emb = discord.Embed(title='Решение Вассермана', value='\u200b', color=0x00FBF0)
        emb.add_field(name=f"{user}", value='\u200b', inline=False)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        await ctx.channel.send(embed=emb)
    except:
        emb = discord.Embed(title='Error', value='\u200b', color=0x008000)
        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
        emb.add_field(name=f"Что-то сломалось", value='\u200b', inline=False)
        await ctx.channel.send(embed=emb)

@bot.command(pass_context=True)
async def mute(ctx):
    try:
        connection = await connectsql()
        with connection:
            cur = connection.cursor()
            insert_query = "SELECT * FROM mute"
            cur.execute(insert_query)
            rows = cur.fetchall()
            if rows != ():
                emb = discord.Embed(title=f"Список пользователей с выключеным чатом:", value='\u200b', color=0xff0000)
                emb.add_field(name=f'Всего записей: {len(rows)}', value='\u200b', inline=False)
                count = 1
                for i in rows:
                    a = i['login']
                    emb.add_field(name=f'{count}. {a}', value='\u200b', inline=False)
                    count += 1
                emb.set_author(name=f"Список предоставлен: {bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
            else:
                emb = discord.Embed(title=f"У всех включен чат", value='\u200b', color=0xff0000)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
    except:
        pass

@bot.command(pass_context=True)
async def muteadd(ctx, arg):
    try:
        if ctx.message.author.id == 318720256795344896:
            connection = await connectsql()
            with connection.cursor() as cursor:
                cur = connection.cursor()
                insert_query = "SELECT * FROM mute"
                cur.execute(insert_query)
                rows = cur.fetchall()
                if rows != ():
                    for i in rows:
                        a = i['login']
                        if a == arg:
                            emb = discord.Embed(title=f'Ага, держи карман шире, он там уже есть', value='\u200b',
                                                color=0xff0000)
                            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                            await ctx.channel.send(embed=emb)
                            return
                insert_query = f"INSERT INTO mute (login) VALUES ('{arg}');"
                cursor.execute(insert_query)
                connection.commit()
                emb = discord.Embed(title=f'{arg} успешно добавлен в мут', value='\u200b', color=0x00FF00)
                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                await ctx.channel.send(embed=emb)
        else:
            emb = discord.Embed(title='Ошибка', value='\u200b', color=0x008000)
            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
            emb.add_field(name=f"Недостаточно прав", value='\u200b', inline=False)
            await ctx.channel.send(embed=emb)
    except:
        pass

@bot.command(pass_context=True)
async def unmute(ctx, arg):
    connection = await connectsql()
    try:
        if ctx.message.author.id == 318720256795344896:
            with connection.cursor() as cursor:
                insert_query = f"SELECT * FROM mute"
                cursor.execute(insert_query)
                rows = cursor.fetchall()
                if rows != ():
                    if arg == 'all':
                        for i in rows:
                            user = i['login']
                            insert_query = f"DELETE FROM mute WHERE login = ('{user}');"
                            cursor.execute(insert_query)
                            connection.commit()
                        emb = discord.Embed(title=f'Список mute был успешно очищен', value='\u200b', color=0x00FF00)
                        emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                        emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                        await ctx.channel.send(embed=emb)
                    else:
                        arg = str(arg)
                        for i in rows:
                            user = i['login']
                            if user == arg:
                                insert_query = f"DELETE FROM mute WHERE login = ('{arg}');"
                                cursor.execute(insert_query)
                                connection.commit()
                                emb = discord.Embed(title=f'{arg} успешно удален из mute', value='\u200b',
                                                    color=0x00FF00)
                                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                                await ctx.channel.send(embed=emb)
                            else:
                                emb = discord.Embed(title=f'Данному пользователю не выключен чат', value='\u200b',
                                                    color=0xff0000)
                                emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                                emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                                await ctx.channel.send(embed=emb)
                else:
                    emb = discord.Embed(title=f"Список mute пуст", value='\u200b', color=0xff0000)
                    emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
                    emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
                    await ctx.channel.send(embed=emb)
        else:
            emb = discord.Embed(title='Ошибка', value='\u200b', color=0x008000)
            emb.set_author(name=f"{bot.user}", icon_url=bot.user.avatar_url)
            emb.set_footer(text=f"Bot powered by: Vitaly#1605", icon_url=creator.avatar_url)
            emb.add_field(name=f"Недостаточно прав", value='\u200b', inline=False)
            await ctx.channel.send(embed=emb)

    except:
        pass

async def parser_cbr():
    url = 'https://cbr.ru/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('div', class_='col-xs-9')
    text = []
    for quote in quotes:
        text.append(quote.text)
    return text

async def connectsql():
    connection = pymysql.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.db_name,
        charset=config.charset,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

bot.run(config.TOKEN)