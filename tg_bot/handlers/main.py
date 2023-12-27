from aiogram import types
from aiogram import dispatcher
from aiogram.dispatcher import FSMContext
from tg_bot.states import Add_sound_state
import os, hashlib, uuid, datetime, requests, json
import aiofiles
from sqlalchemy import and_, desc
from tg_bot.models import sessionmaker, engine, Files
from pydub import AudioSegment


async def start_handler(message: types.Message):
    print(message)


async def add_sound_handler(message: types.message, state: FSMContext):
    # print(message)
    name = message.text[11:]
    if name == "":
        await message.answer(
            "Please tell me how to name a sound you want to attach! Tell me /add_sound <sound_name> ❌🤔"
        )
    else:
        await Add_sound_state.add.set()
        async with state.proxy() as data:
            data["name"] = name
        await message.answer("Now, please send me sound with .mp3 coding")


async def get_audio(message: types.Document, state: FSMContext):
    try:
        file_id = message.audio.file_id
        async with state.proxy() as data:
            name = data["name"]
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        print(message.from_user.id)

        if not os.path.exists(f"files/{message.from_user.id}"):
            os.makedirs(f"files/{message.from_user.id}")

        file_name = os.path.basename(file_path)
        local_file_path = f"files/{message.from_user.id}/{file_name}"
        await file.download(destination=local_file_path)

        input_file = local_file_path
        output_file = local_file_path[:-3] + "oga"

        audio = AudioSegment.from_mp3(input_file)
        audio.export(output_file, format="oga")
        # print(output_file)

        Session = sessionmaker()
        session = Session(bind=engine)
        new_file = Files(
            Id_user=message.from_user.id, Name_sound=name, Path=output_file
        )
        session.add(new_file)
        session.commit()
        session.close()

        await message.answer(
            f"Good job! Your sound has been successfully added! Try sending it to somebody using @play command! ✅😎"
        )
        await state.finish()
    except:
        await message.answer("Seems like there is no .mp3 file attached! ❌🧐")
        await state.finish()


async def delete_message(message: types.message):
    name = message.text[14:]
    print(name)
    try:
        Session = sessionmaker()
        session = Session(bind=engine)

        file = (
            session.query(Files)
            .filter(Files.Name_sound == name, Files.Id_user == message.from_user.id)
            .first()
        )
        try:
            os.remove(f"files/{message.from_user.id}{file.Path}")
        except Exception as E:
            print(E)

        session.delete(file)
        session.commit()
        session.close()
        await message.answer("This sound has been successfully deleted! ✅👾")
    except:
        await message.answer(
            "Didn't find file assosiated with entered <sound_name> in my storage! ❌😲"
        )


async def upload_voice_and_get_link(bot, path):
    voice_path = path

    with open(voice_path, "rb") as voice_file:
        voice_message = await bot.send_voice(chat_id="1924535035", voice=voice_file)
        return voice_message.voice.file_id


async def inline_echo(inline_query: types.InlineQuery):
    print(inline_query.query)

    Session = sessionmaker()
    session = Session(bind=engine)
    today = datetime.datetime.today()
    last_files = (
        session.query(Files)
        .filter(Files.Name_sound.like(f"{inline_query.query}%"))
        .filter(Files.Date_genering_id <= (today - datetime.timedelta(days=30)))
        .all()
    )
    for i in last_files:
        file_id = await upload_voice_and_get_link(inline_query.bot, i.Path)
        i.Id_audio = file_id
        i.Date_genering_id = datetime.datetime.now()
    session.add_all(last_files)
    session.commit()

    files = (
        session.query(Files)
        .filter(Files.Id_user == inline_query.from_user.id)
        .filter(Files.Name_sound.like(f"{inline_query.query}%"))
        .all()
    )
    for i in files:
        if i.Id_audio is None:
            file_id = await upload_voice_and_get_link(inline_query.bot, i.Path)
            i.Id_audio = file_id
            i.Date_genering_id = datetime.datetime.now()
    session.add_all(files)
    session.commit()

    files = (
        session.query(Files)
        .filter(
            and_(
                Files.Id_user == inline_query.from_user.id,
                Files.Name_sound.ilike(f"{inline_query.query}%"),
            )
        )
        .all()
    )
    session.close()

    res = []
    for i in files:
        voice = types.InlineQueryResultVoice(
            id=i.Id,
            title=i.Name_sound,
            voice_file_id=i.Id_audio,
        )
        res.append(voice)
    if inline_query.query == "":
        await inline_query.bot.answer_inline_query(
            inline_query.id,
            results=res,
            cache_time=1,
            switch_pm_text=f"All sounds:",
            switch_pm_parameter="start",
            is_personal=False,
            next_offset="",
        )
    if res == []:
        await inline_query.bot.answer_inline_query(
            inline_query.id,
            results=res,
            cache_time=1,
            switch_pm_text=f"Didn't find file assosiated with entered {inline_query.query} in my storage! ❌😲",
            switch_pm_parameter=f"start",
            is_personal=False,
            next_offset="",
        )
    else:
        await inline_query.bot.answer_inline_query(
            inline_query.id,
            results=res,
            cache_time=1,
            switch_pm_text=f"All sounds, that name starts with: {inline_query.query}",
            switch_pm_parameter="start",
            is_personal=True,
            next_offset="",
        )


def register_main_handlers(dp: dispatcher):
    dp.register_message_handler(start_handler, text="/start")
    dp.register_message_handler(add_sound_handler, commands=["add_sound"])
    dp.register_message_handler(delete_message, commands=["delete_sound"], state="*")
    dp.register_message_handler(
        get_audio, content_types=types.ContentType.ANY, state=Add_sound_state.add
    )
    dp.register_inline_handler(inline_echo)

    # dp.on(types.Document, get_audio)
