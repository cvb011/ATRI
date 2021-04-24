import json
import re
import asyncio
from pathlib import Path
from random import choice, randint

from nonebot.adapters.cqhttp import Bot, MessageEvent, GroupMessageEvent
from nonebot.adapters.cqhttp.message import Message, MessageSegment

from ATRI.service import Service as sv
from ATRI.utils.limit import is_too_exciting
from ATRI.rule import is_in_service
from ATRI.utils.request import post_bytes
from ATRI.utils.translate import to_simple_string
from ATRI.exceptions import RequestTimeOut


__doc__ = """
看不懂的笑话
权限组：所有人
用法：
  来句笑话
"""

get_laugh = sv.on_command(
    cmd='来句笑话',
    docs=__doc__,
    rule=is_in_service('来句笑话')
)

@get_laugh.handle()
async def _get_laugh(bot: Bot, event: MessageEvent) -> None:
    user_name = event.sender.nickname
    laugh_list = []
    
    FILE = Path('.') / 'ATRI' / 'data' / 'database' / 'funny' / 'laugh.txt'
    with open(FILE, 'r', encoding='utf-8') as r:
        for line in r:
            laugh_list.append(line.strip('\n'))
    
    result = choice(laugh_list)
    await get_laugh.finish(result.replace("%name", user_name))


me_to_you = sv.on_message()

@me_to_you.handle()
async def _me_to_you(bot: Bot, event: MessageEvent) -> None:
    if randint(0, 15) == 5:
        msg = str(event.message)
        if "我" in msg and "CQ" not in msg:
            await me_to_you.finish(msg.replace("我", "你"))


__doc__ = """
随机选择一位群友成为我的老婆！
权限组：所有人
用法：
  抽老婆
"""

roll_wife = sv.on_command(
    cmd='抽老婆',
    docs=__doc__,
    rule=is_in_service('抽老婆')
)

@roll_wife.handle()
async def _roll_wife(bot: Bot, event: GroupMessageEvent) -> None:
    user = event.user_id
    group = event.group_id
    
    user_name = await bot.get_group_member_info(group_id=group,
                                                user_id=user)
    user_name = user_name['nickname']
    run = await is_too_exciting(user, group, 5, True)
    if not run:
        return
    
    luck_list = await bot.get_group_member_list(group_id=group)
    luck_user = choice(luck_list)
    luck_qq = luck_user['user_id']
    luck_user = luck_user['nickname']
    msg = (
        "5秒后咱将随机抽取一位群友成为\n"
        f"{user_name} 的老婆！究竟是谁呢~？"
    )
    await bot.send(event, msg)
    await asyncio.sleep(5)
    msg = (
        f"> {luck_user}({luck_qq})\n"
        f"恭喜成为 {user_name} 的老婆~⭐"
    )
    await bot.send(event, msg)


__doc__ = """
伪造转发
权限组：所有人
用法：
  /fakemsg qq*name*msg...
补充:
  qq: QQ号
  name: 消息中的ID
  msg: 对应信息
示例:
  /fakemsg 123456789*生草人*草 114514*仙贝*臭死了
"""

fake_msg = sv.on_command(
    cmd="/fakemsg",
    docs=__doc__,
    rule=is_in_service('fakemsg')
)

@fake_msg.handle()
async def _fake_msg(bot: Bot, event: GroupMessageEvent) -> None:
    msg = str(event.message).split(' ')
    user = event.user_id
    group = event.group_id
    node = []
    check = await is_too_exciting(user, group, 1, True)
    
    if check:
        for i in msg:
            args = i.split('*')
            qq = args[0]
            name = args[1].replace('&#91;', '[')
            name = name.replace('&#93;', ']')
            repo = args[2].replace('&#91;', '[')
            repo = repo.replace('&#93;', ']')
            dic = {
                "type": "node",
                "data": {
                    "name": name,
                    "uin": qq,
                    "content": repo
                }
            }
            node.append(dic)
    await bot.send_group_forward_msg(group_id=group, messages=node)


EAT_URL = "https://wtf.hiigara.net/api/run/{}"

eat_wat = sv.on_regex(r"[今|明|后|大后]天(.*?)吃什么", rule=is_in_service('今天吃什么'))

@eat_wat.handle()
async def _eat(bot: Bot, event: MessageEvent) -> None:
    msg = str(event.message).strip()
    user = event.user_id
    user_n = event.sender.nickname
    arg = re.findall(r"[今|明|后|大后]天(.*?)吃什么", msg)[0]
    nd = re.match(r"[今|明|后|大后][天]", msg)[0]
    
    if arg == "中午":
        a = f"LdS4K6/{randint(0, 999999)}"
        url = EAT_URL.format(a)
        params = {"event": "ManualRun"}
        try:
            data = json.loads(await post_bytes(url, params))
        except RequestTimeOut:
            raise RequestTimeOut('Request failed!')
        
        text = to_simple_string(data['text']).replace('今天', nd)
        get_a = re.search(r"非常(.*?)的", text)[0]
        result = f"> {MessageSegment.at(user)}\n" + text.replace(get_a, '')
    
    elif arg == "晚上":
        a = f"KaTMS/{randint(0, 999999)}"
        url = EAT_URL.format(a)
        params = {"event": "ManualRun"}
        try:
            data = json.loads(await post_bytes(url, params))
        except RequestTimeOut:
            raise RequestTimeOut('Request failed!')
        
        text = to_simple_string(data['text']).replace('今天', '')
        result = f"> {MessageSegment.at(user)}\n" + text
    
    else:
        rd = randint(1, 10)
        if rd == 5:
            result = "吃我吧 ❤"
        else:
            a = f"JJr1hJ/{randint(0, 999999)}"
            url = EAT_URL.format(a)
            params = {"event": "ManualRun"}
            try:
                data = json.loads(await post_bytes(url, params))
            except RequestTimeOut:
                raise RequestTimeOut('Request failed!')
            
            text = to_simple_string(data['text']).replace('今天', nd)
            get_a = re.match(r"(.*?)的智商", text)[0]
            result = f"> {MessageSegment.at(user)}\n" + text.replace(get_a, f'{user_n}的智商')
    
    await eat_wat.finish(Message(result))