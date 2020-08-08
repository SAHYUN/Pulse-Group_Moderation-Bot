# Made by 사현#0903

import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import sqlite3
import os


client = commands.Bot(command_prefix= '=디케 ')
client.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

conn = sqlite3.connect("main.db")

cur = conn.cursor()


@client.event
async def on_ready():
    print("=========================")
    print("Bot is ready")
    print(f"Client name :: {client.user.name}")
    print(f"Client ID :: {client.user.id}")
    print("=========================")
    check_mutes.start()

    game = discord.Game("=디케 도움말")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.command(name= "청소")
@commands.has_permissions(administrator= True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit= amount)


@client.command(name= "도움말")
async def help(ctx):
    embed = discord.Embed(title= "도움말", colour= discord.Colour.blue())
    embed.add_field(name= "관리자 명령어", 
    value= "``청소 갯수``, ``개인DM @멘션 텍스트``,\n ``업데이트 #채널태그 제목 버전``, ``공지 #채널태그 제목``,\n ``이벤트등록 이벤트제목``, ``이벤트삭제 이벤트제목``,\n ``유저메모 @멘션 텍스트``, ``메모삭제 @멘션``, \n``유저정보 @멘션``, ``밴 @멘션 사유``, \n``언밴 @멘션 사유``, ``킥 @멘션 사유``, \n``경고 @멘션 사유``, ``경고삭제 경고ID``,\n ``경고초기화 @멘션``, ``채금 @멘션 영구/0h 0m 0s 사유``, ``채금종료 @멘션``", inline= False)
    embed.add_field(name= "유저 명령어", value= "``이벤트``, ``서버주소``, ``도움말``, ``문의 할말``", inline= False)

    await ctx.send(embed= embed)


@client.command(name= "개인DM")
@commands.has_permissions(administrator= True)
async def send_dm(ctx, user: discord.Member, *, text):
    await user.send(embed= discord.Embed(title= "메시지가 도착하였습니다.", description= text, colour= discord.Colour.blue()))
    await ctx.send("> 전송이 완료되었습니다.")


@client.command(name= "업데이트")
@commands.has_permissions(administrator= True)
async def update(ctx, channel: discord.TextChannel, *, title = "업데이트", version = "1"):
    await ctx.send("> 내용을 1분 이내에 작성해주세요.")

    try:
        msg = await client.wait_for('message', timeout=60, check= lambda m: m.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("> 업데이트 작성이 취소되었습니다.")
    else:
        embed = discord.Embed(title= title, description= msg.content, colour= discord.Colour.blue(), timestamp= datetime.datetime.now())
        embed.set_footer(text= f"버전 | {version}")
        await channel.send(embed= embed)


@client.command(name= "공지")
@commands.has_permissions(administrator= True)
async def broadcast(ctx, channel: discord.TextChannel, *, title = "공지"):
    await ctx.send("> 내용을 1분 이내에 작성해주세요.")

    try:
        msg = await client.wait_for('message', timeout=60, check= lambda m: m.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("> 공지사항 작성이 취소되었습니다.")
    else:
        embed = discord.Embed(title= title, description= msg.content, colour= discord.Colour.blue(), timestamp= datetime.datetime.now())
        embed.set_footer(text= ctx.author.name, icon_url= ctx.author.avatar_url)
        await channel.send(embed= embed)


@client.command(name= "이벤트등록")
@commands.has_permissions(administrator= True)
async def add_event(ctx, *, title = "이벤트"):
    await ctx.send("> 이벤트 기간을 1분 이내에 작성해주세요.")

    try:
        during = await client.wait_for('message', timeout= 60, check= lambda m: m.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("> 이벤트 등록이 취소되었습니다.")
        return None

    await ctx.send("> 이벤트 내용을 1분 이내에 작성해주세요.")

    try:
        msg = await client.wait_for('message', timeout=60, check= lambda m: m.author == ctx.author)
    except asyncio.TimeoutError:
        await ctx.send("> 이벤트 등록이 취소되었습니다.")
        return None
    
    cur.execute("INSERT INTO EVENT(title, content, during) VALUES (?, ?, ?)", (title, msg.content, during.content))
    conn.commit()

    await ctx.send("> 이벤트 등록이 완료되었습니다.")


@client.command(name= "이벤트삭제")
@commands.has_permissions(administrator= True)
async def delete_event(ctx, title):
    try:
        cur.execute(f"DELETE FROM EVENT WHERE title= {title}")
        conn.commit()
    except:
        await ctx.send(f"> 일치하는 이벤트가 존재하지 않습니다. ( {title} )")
        return None

    await ctx.send(f"> {title} 이벤트가 삭제 되었습니다.")


@client.command(name= "유저메모")
@commands.has_permissions(administrator= True)
async def memo(ctx, member: discord.Member, *, content):
    cur.execute(f"SELECT * FROM memo WHERE user_id= {member.id}")
    check = cur.fetchone()

    if check == None:
        cur.execute(f"INSERT INTO memo VALUES (?, ?)", (member.id, content))
        conn.commit()
    else:
        cur.execute(f"UPDATE memo SET content = {content} WHERE user_id = {member.id}")
        conn.commit()
    
    await ctx.send("> 메모 등록이 완료되었습니다.")


@client.command(name= "메모삭제")
@commands.has_permissions(administrator= True)
async def delete_memo(ctx, member: discord.Member):
    cur.execute(f"DELETE FROM memo WHERE user_id= {member.id}")
    conn.commit()

    await ctx.send("> 메모가 삭제되었습니다.")


@client.command(name= "유저정보")
@commands.has_permissions(administrator= True)
async def user_info(ctx, member: discord.Member):
    cur.execute(f"SELECT * FROM WARNS WHERE user_id= {member.id}")
    warns = cur.fetchall()

    warn_count = 0
    reasons = list()
    for i in warns:
        warn_count += 1
        reasons.append(f"( ID : {i[0]} )경고 {client.get_user(i[1])} {i[2]}")

    cur.execute(f"SELECT * FROM MUTES WHERE user_id= {member.id}")
    mutes = cur.fetchall()

    for i in mutes:
        reasons.append(f"채팅금지 {client.get_user(i[0])} {i[1]} {i[2]}")

    reasons = '\n'.join(reasons)

    memo = "등록된 메모가 없습니다."
    cur.execute(f"SELECT * FROM memo WHERE user_id= {member.id}")
    check_memo = cur.fetchone()

    if check_memo:
        memo = check_memo[1]
    
    cur.execute(f"SELECT * FROM ON_MUTED WHERE user_id= {member.id}")
    check_mute = cur.fetchone()

    try:
        check_mute = f"채팅금지 {check_mute[1]}"
    except:
        check_mute = "진행중인 처벌이 없습니다."

    embed = discord.Embed(title= f"{member.name} 님의 정보", colour= discord.Colour.blue())
    embed.add_field(name= "현재 경고 횟수", value= f"{warn_count} / 3")
    embed.add_field(name= "처벌 기록", value= f"```{reasons}```", inline= False)
    embed.add_field(name= "받고있는 처벌", value= f"```{check_mute}```", inline= False)
    embed.add_field(name= "메모", value= f"```{memo}```", inline= False)
    embed.set_footer(text= f"{member.name} | {member.id}", icon_url= member.avatar_url)

    await ctx.send(embed= embed)


@client.command(name= "이벤트")
async def check_event(ctx):

    cur.execute("SELECT * FROM EVENT")
    events = cur.fetchall()

    if events == []:
        await ctx.send("> 등록된 이벤트가 없습니다.")
        await ctx.send(ctx.author.mention)
        return None

    for i in events:
        embed = discord.Embed(title= i[0], description= i[1], colour= discord.Colour.blue())
        embed.set_footer(text= f"이벤트 기간 | {i[2]}")

        await ctx.send(embed= embed)
    
    await ctx.send(ctx.author.mention)


@client.command(name= "문의")
async def mun(ctx, *, content):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        embed = discord.Embed(title= f"{ctx.author.name} 님의 문의입니다.", description= content, colour= discord.Colour.blue(), timestamp= datetime.datetime.now())
        embed.add_field(name= "유저 멘션", value= ctx.author.mention, inline= False)
        embed.set_footer(text= ctx.author.id, icon_url= ctx.author.avatar_url)
        await client.get_user(586165160821915653).send(embed= embed)


@client.command(name= "서버주소")
async def link(ctx):
    await ctx.send(embed= discord.Embed(title= "farmparty.me"))
    

@tasks.loop(seconds= 2)
async def check_mutes():
    cur.execute("SELECT * FROM ON_MUTED")
    mutes = cur.fetchall()
    
    for i in mutes:

        role = discord.utils.get(client.get_guild(i[2]).roles, name= "Muted")

        date = datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S')

        if date < datetime.datetime.now():
            await client.get_guild(i[2]).get_member(i[0]).remove_roles(role)
            cur.execute("DELETE FROM ON_MUTED WHERE user_id=" + str(i[0]))
            conn.commit()




client.run("")


