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
    text = """Hi there! There is a list of my functions:\n\n/add_sound <sound_name>. Use it in order to add a new sound into my storage. This sound will be available by this name later on. ➕\n\n/list_sounds. Use it to view the list of sounds you added earlier that are currently available. 📌\n\n/delete_sound <sound_name>. I suppose it's pretty clear what this command does 🧐\n\n(inline) @myBotName <sound_name>. Use this command from any chat you want and choose your <sound_name>. I will send a voice message that contains your .mp3 file assosiated with this name. 🔊"""
    await message.answer(text)


async def add_sound_handler(message: types.message, state: FSMContext):
    name = message.text[11:]
    Session = sessionmaker()
    session = Session(bind=engine)
    sound_this_name = (
        session.query(Files)
        .filter(Files.Id_user == message.from_user.id, Files.Name_sound == name)
        .all()
    )
    session.close()
    if name == "":
        await message.answer(
            "Please tell me how to name a sound you want to attach! Tell me /add_sound <sound_name> ❌🤔"
        )
    elif sound_this_name != []:
        await message.answer(
            "I already have a sound with that name! Please come up with something else! ❌😒"
        )
    else:
        await Add_sound_state.add.set()
        async with state.proxy() as data:
            data["name"] = name
        await message.answer("Now, please send me a sound with .mp3 extension")


async def get_audio(message: types.Document, state: FSMContext):
    try:
        file_id = message.audio.file_id
        async with state.proxy() as data:
            name = data["name"]
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        if not os.path.exists(f"files/{message.from_user.id}"):
            os.makedirs(f"files/{message.from_user.id}")

        file_name = os.path.basename(file_path)
        local_file_path = f"files/{message.from_user.id}/{file_name}"
        await file.download(destination=local_file_path)

        input_file = local_file_path

        size = os.path.getsize(input_file)

        Session = sessionmaker()
        session = Session(bind=engine)
        all_media = (
            session.query(Files).filter(Files.Id_user == message.from_user.id).all()
        )
        all_size = 0
        for i in all_media:
            all_size += i.Size_audio

        if size + all_size < 1024 * 1024 * 100:  # - 100 Mb
            new_file = Files(
                Id_user=message.from_user.id,
                Name_sound=name,
                Path=local_file_path,
                Size_audio=size,
            )
            session.add(new_file)
            session.commit()
            session.close()

            await message.answer(
                f"Good job! Your sound has been successfully added! Try sending it to somebody using @MyBotName inline command! ✅😎"
            )
            await state.finish()
        else:
            session.close()
            await message.answer(
                "Your disk space limit is reached! Try deleting some unused sounds first! You can find list with all your sounds: /list_sounds ❌😢"
            )
            await state.finish()
    except:
        await message.answer("Seems like there is no .mp3 file attached! ❌🧐")
        await state.finish()


async def delete_message(message: types.message):
    name = message.text[14:]
    try:
        Session = sessionmaker()
        session = Session(bind=engine)

        file = (
            session.query(Files)
            .filter(Files.Name_sound == name, Files.Id_user == message.from_user.id)
            .first()
        )
        try:
            os.remove(f"{file.Path}")
        except Exception as E:
            pass

        session.delete(file)
        session.commit()
        session.close()
        await message.answer("This sound has been successfully deleted! ✅👾")
    except:
        await message.answer(
            f"""Didn't find a file assosiated with entered name "{name}" in my storage! ❌😲"""
        )


async def upload_voice_and_get_link(bot, path, chat_id):
    voice_path = path

    with open(voice_path, "rb") as voice_file:
        voice_message = await bot.send_voice(chat_id=chat_id, voice=voice_file)
        return voice_message.voice.file_id


async def sound_list(message: types.Message):
    Session = sessionmaker()
    session = Session(bind=engine)

    all_media = session.query(Files).filter(Files.Id_user == message.from_user.id).all()

    session.close()

    if all_media != []:
        text = "Your sounds are:\n"

        for i in all_media:
            text += (
                f"📌 {i.Name_sound} -  <b>"
                + "{:.2f}".format(i.Size_audio / 1024 / 1024)
                + " Mb</b>\n"
            )
        await message.answer(text, parse_mode=types.ParseMode.HTML)
    else:
        await message.answer(
            "There are not any sounds in your collection\nFeel free to add ones using /add_sound <sound_name>🧐"
        )


async def inline_echo(inline_query: types.InlineQuery):
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
        local_file_path = i.Path
        input_file = local_file_path
        output_file = local_file_path[:-3] + "oga"
        try:
            audio = AudioSegment.from_mp3(input_file)
            audio.export(output_file, format="oga")
        except:
            pass
        os.remove(output_file)
    session.add_all(last_files)
    session.commit()

    files = (
        session.query(Files)
        .filter(Files.Id_user == inline_query.from_user.id)
        .filter(Files.Name_sound.like(f"{inline_query.query}%"))
        .all()
    )
    for i in files:
        if i.Id_audio is None or i.Id_audio == "":
            local_file_path = i.Path
            input_file = local_file_path
            output_file = local_file_path[:-3] + "oga"
            try:
                audio = AudioSegment.from_mp3(input_file)
                audio.export(output_file, format="oga")
            except Exception as E:
                print(E)
            file_id = await upload_voice_and_get_link(inline_query.bot, output_file, inline_query.from_user.id)
            i.Id_audio = file_id
            i.Date_genering_id = datetime.datetime.now()
            os.remove(output_file)
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
        voice = types.InlineQueryResultCachedVoice(
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
            switch_pm_parameter="list_sounds",
            is_personal=False,
            next_offset="",
        )
    if res == []:
        await inline_query.bot.answer_inline_query(
            inline_query.id,
            results=res,
            cache_time=1,
            switch_pm_text=f"""Didn't find a file assosiated with entered name "{inline_query.query}" in my storage! ❌😲""",
            switch_pm_parameter=f"list_sounds",
            is_personal=False,
            next_offset="",
        )
    else:
        await inline_query.bot.answer_inline_query(
            inline_query.id,
            results=res,
            cache_time=1,
            switch_pm_text=f"All sounds, that name starts with: {inline_query.query}",
            switch_pm_parameter="list_sounds",
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
    dp.register_message_handler(sound_list, commands=["list_sounds"], state="*")
    dp.register_inline_handler(inline_echo)
