from pymongo import MongoClient
from telethon import *
from telethon.tl import *

from GroupMenter import BOT_ID, MONGO_DB_URI
from GroupMenter import telethn as tbot
from GroupMenter.events import register

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["darkuserbot"]
approved_users = db.approve
dbb = client["darkuserbot"]
poll_id = dbb.pollid


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None


@register(pattern="^/poll (.*)")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    try:
        quew = event.pattern_match.group(1)
    except Exception:
        await event.reply("soru nerede?")
        return
    if "|" in quew:
        secrets, quess, options = quew.split("|")
    secret = secrets.strip()

    if not secret:
        await event.reply("Anket yapmak için 5 basamaklı bir anket kimliğine ihtiyacım var")
        return

    try:
        secret = str(secret)
    except ValueError:
        await event.reply("Anket kimliği yalnızca sayıları içermelidir")
        return

    # print(secret)

    if len(secret) != 5:
        await event.reply("Anket kimliği 5 basamaklı bir tam sayı olmalıdır")
        return

    allpoll = poll_id.find({})
    # print(secret)
    for c in allpoll:
        if event.sender_id == c["user"]:
            await event.reply(
                "Lütfen yeni bir anket oluşturmadan önce önceki anketi durdurun!"
            )
            return
    poll_id.insert_one({"user": event.sender_id, "pollid": secret})

    ques = quess.strip()
    option = options.strip()
    quiz = option.split(" ")[1 - 1]
    if "True" in quiz:
        quizy = True
        if "@" in quiz:
            one, two = quiz.split("@")
            rightone = two.strip()
        else:
            await event.reply(
                "True@1, True@3 vb. gibi soru numarası ile doğru cevabı seçmeniz gerekiyor."
            )
            return

        quizoptionss = []
        try:
            ab = option.split(" ")[4 - 1]
            cd = option.split(" ")[5 - 1]
            quizoptionss.append(types.PollAnswer(ab, b"1"))
            quizoptionss.append(types.PollAnswer(cd, b"2"))
        except Exception:
            await event.reply("Anket oluşturmak için en az iki seçeneğe ihtiyacınız var")
            return
        try:
            ef = option.split(" ")[6 - 1]
            quizoptionss.append(types.PollAnswer(ef, b"3"))
        except Exception:
            ef = None
        try:
            gh = option.split(" ")[7 - 1]
            quizoptionss.append(types.PollAnswer(gh, b"4"))
        except Exception:
            gh = None
        try:
            ij = option.split(" ")[8 - 1]
            quizoptionss.append(types.PollAnswer(ij, b"5"))
        except Exception:
            ij = None
        try:
            kl = option.split(" ")[9 - 1]
            quizoptionss.append(types.PollAnswer(kl, b"6"))
        except Exception:
            kl = None
        try:
            mn = option.split(" ")[10 - 1]
            quizoptionss.append(types.PollAnswer(mn, b"7"))
        except Exception:
            mn = None
        try:
            op = option.split(" ")[11 - 1]
            quizoptionss.append(types.PollAnswer(op, b"8"))
        except Exception:
            op = None
        try:
            qr = option.split(" ")[12 - 1]
            quizoptionss.append(types.PollAnswer(qr, b"9"))
        except Exception:
            qr = None
        try:
            st = option.split(" ")[13 - 1]
            quizoptionss.append(types.PollAnswer(st, b"10"))
        except Exception:
            st = None

    elif "False" in quiz:
        quizy = False
    else:
        await event.reply("Yanlış argümanlar sağlandı !")
        return

    pvote = option.split(" ")[2 - 1]
    if "True" in pvote:
        pvoty = True
    elif "False" in pvote:
        pvoty = False
    else:
        await event.reply("Yanlış argümanlar sağlandı !")
        return
    mchoice = option.split(" ")[3 - 1]
    if "True" in mchoice:
        mchoicee = True
    elif "False" in mchoice:
        mchoicee = False
    else:
        await event.reply("Yanlış argümanlar sağlandı !")
        return
    optionss = []
    try:
        ab = option.split(" ")[4 - 1]
        cd = option.split(" ")[5 - 1]
        optionss.append(types.PollAnswer(ab, b"1"))
        optionss.append(types.PollAnswer(cd, b"2"))
    except Exception:
        await event.reply("Anket oluşturmak için en az iki seçeneğe ihtiyacınız var")
        return
    try:
        ef = option.split(" ")[6 - 1]
        optionss.append(types.PollAnswer(ef, b"3"))
    except Exception:
        ef = None
    try:
        gh = option.split(" ")[7 - 1]
        optionss.append(types.PollAnswer(gh, b"4"))
    except Exception:
        gh = None
    try:
        ij = option.split(" ")[8 - 1]
        optionss.append(types.PollAnswer(ij, b"5"))
    except Exception:
        ij = None
    try:
        kl = option.split(" ")[9 - 1]
        optionss.append(types.PollAnswer(kl, b"6"))
    except Exception:
        kl = None
    try:
        mn = option.split(" ")[10 - 1]
        optionss.append(types.PollAnswer(mn, b"7"))
    except Exception:
        mn = None
    try:
        op = option.split(" ")[11 - 1]
        optionss.append(types.PollAnswer(op, b"8"))
    except Exception:
        op = None
    try:
        qr = option.split(" ")[12 - 1]
        optionss.append(types.PollAnswer(qr, b"9"))
    except Exception:
        qr = None
    try:
        st = option.split(" ")[13 - 1]
        optionss.append(types.PollAnswer(st, b"10"))
    except Exception:
        st = None

    if pvoty is False and quizy is False and mchoicee is False:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(id=12345, question=ques, answers=optionss, quiz=False)
            ),
        )

    if pvoty is True and quizy is False and mchoicee is True:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=True,
                    public_voters=True,
                )
            ),
        )

    if pvoty is False and quizy is False and mchoicee is True:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=True,
                    public_voters=False,
                )
            ),
        )

    if pvoty is True and quizy is False and mchoicee is False:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=False,
                    public_voters=True,
                )
            ),
        )

    if pvoty is False and quizy is True and mchoicee is False:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345, question=ques, answers=quizoptionss, quiz=True
                ),
                correct_answers=[f"{rightone}"],
            ),
        )

    if pvoty is True and quizy is True and mchoicee is False:
        await tbot.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=quizoptionss,
                    quiz=True,
                    public_voters=True,
                ),
                correct_answers=[f"{rightone}"],
            ),
        )

    if pvoty is True and quizy is True and mchoicee is True:
        await event.reply("Test moduyla çoklu oylama kullanamazsınız")
        return
    if pvoty is False and quizy is True and mchoicee is True:
        await event.reply("Test moduyla çoklu oylama kullanamazsınız")
        return


@register(pattern="^/stoppoll(?: |$)(.*)")
async def stop(event):
    secret = event.pattern_match.group(1)
    # print(secret)
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return

    if not event.reply_to_msg_id:
        await event.reply("Lütfen durdurmak için bir anketi yanıtlayın")
        return

    if input is None:
        await event.reply("anket kimliği nerede ?")
        return

    try:
        secret = str(secret)
    except ValueError:
        await event.reply("Anket kimliği yalnızca sayıları içermelidir")
        return

    if len(secret) != 5:
        await event.reply("Anket kimliği 5 basamaklı bir tam sayı olmalıdır")
        return

    msg = await event.get_reply_message()

    if str(msg.sender_id) != str(BOT_ID):
        await event.reply(
            "Bu işlemi bu ankette yapamam.\nMuhtemelen benim tarafımdan oluşturulmamıştır."
        )
        return
    print(secret)
    if msg.poll:
        allpoll = poll_id.find({})
        for c in allpoll:
            if not event.sender_id == c["user"] and not secret == c["pollid"]:
                await event.reply(
                    "Hata, ya bu anketi oluşturmadınız ya da yanlış anket kimliği verdiniz"
                )
                return
        if msg.poll.poll.closed:
            await event.reply("Hata, anket zaten kapalı.")
            return
        poll_id.delete_one({"user": event.sender_id})
        pollid = msg.poll.poll.id
        await msg.edit(
            file=types.InputMediaPoll(
                poll=types.Poll(id=pollid, question="", answers=[], closed=True)
            )
        )
        await event.reply("Anket başarıyla durduruldu")
    else:
        await event.reply("Bu bir anket değil")


@register(pattern="^/forgotpollid$")
async def stop(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    allpoll = poll_id.find({})
    for c in allpoll:
        if event.sender_id == c["user"]:
            try:
                poll_id.delete_one({"user": event.sender_id})
                await event.reply("Bitti, şimdi yeni bir anket oluşturabilirsiniz.")
            except Exception:
                await event.reply("Henüz bir anket oluşturmamışsınız gibi görünüyor !")


__help__ = """
Artık Group Menter ile anonim olarak anket gönderebilirsiniz
İşte bunu nasıl yapabilirsiniz:
**Parametreler** -
 ❍ poll-id - bir anket kimliği 5 basamaklı rastgele bir tam sayıdan oluşur, önceki anketinizi durdurduğunuzda bu kimlik otomatik olarak sistemden kaldırılır
 ❍ question - sormak istediğiniz soru
 ❍ <True@optionnumber/False>(1) - test modu, doğru cevabı "@" ile belirtmelisiniz, örneğin: "True@1" veya "True@2"
 ❍ <Doğru/Yanlış>(2) - genel oylar
 ❍ <Doğru/Yanlış>(3) - çoktan seçmeli
**Sözdizimi** -
`/poll <poll-id> <soru> | <Doğru@seçenek numarası/Yanlış> <Doğru/Yanlış> <Doğru/Yanlış> <seçenek1> <seçenek2> ... <seçenek10>`a kadar
**Örnekler** -
`/poll 12345 | iyi miyim? | Yanlış Yanlış Yanlış evet hayır`
`/poll 12345 | iyi miyim? | Doğru@1 Yanlış Yanlış evet hayır`
**Bir anketi durdurmak için**
Anketi durdurmak için `/stoppoll <poll-id>` ile anketi yanıtlayın
**NOT**
Anket kimliğinizi unuttuysanız veya bir önceki anket türünü `/forgotpollid` durduramamak için anketi sildiyseniz, bu anket kimliğini sıfırlayacaktır, önceki ankete erişiminiz olmayacaktır!
"""


__mod_name__ = "ANKET"
