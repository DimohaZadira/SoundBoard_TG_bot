import datetime
import os

from aiogram import Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from pydub import AudioSegment
from sqlalchemy import and_

from soundboard_tg_bot.tg_bot.models import Files, engine, sessionmaker
from soundboard_tg_bot.tg_bot.states import Add_sound_state


class ExpectException(Exception):
    pass


def expect[T](elem: T | None, error: str = "Value is None") -> T:
    if elem is None:
        raise ExpectException(error)
    return elem


async def upload_voice_and_get_link(bot, path, chat_id):
    # voice_path = path
    voice_message = await bot.send_voice(chat_id=chat_id, voice=FSInputFile(path))
    return voice_message.voice.file_id


def register_main_handlers(dp: Dispatcher):
    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        text = """Hi there! There is a list of my functions:\n\n/add_sound <sound_name>. Use it in order to add a new sound into my storage. This sound will be available by this name later on. ➕\n\n/list_sounds. Use it to view the list of sounds you added earlier that are currently available. 📌\n\n/delete_sound <sound_name>. I suppose it's pretty clear what this command does 🧐\n\n(inline) @myBotName <sound_name>. Use this command from any chat you want and choose your <sound_name>. I will send a voice message that contains your .mp3 file assosiated with this name. 🔊"""
        await message.answer(text)

    @dp.message(Command("add_sound"))
    async def add_sound_handler(message: types.Message, state: FSMContext):
        name = expect(message.text)[11:]
        Session = sessionmaker()
        session = Session(bind=engine)
        sound_this_name = (
            session.query(Files)
            .filter(
                Files.Id_user == expect(message.from_user).id, Files.Name_sound == name
            )
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
            # await Add_sound_state.add.set()
            await state.set_state(Add_sound_state.add)
            # async with state.proxy() as data:
            #     data["name"] = name
            await state.update_data(name=name)
            await message.answer("Now, please send me a sound with .mp3 extension")

    @dp.message(Add_sound_state.add)
    async def get_audio(message: types.Message, state: FSMContext):
        try:
            file_id = expect(message.audio).file_id
            data = await state.get_data()
            file = await expect(message.bot).get_file(file_id)
            file_path = expect(file.file_path)

            user_id = expect(message.from_user).id
            if not os.path.exists(f"files/{user_id}"):
                os.makedirs(f"files/{user_id}")

            file_name = os.path.basename(file_path)
            local_file_path = f"files/{user_id}/{file_name}"
            await expect(message.bot).download_file(file_path, local_file_path)

            input_file = local_file_path

            size = os.path.getsize(input_file)

            Session = sessionmaker()
            session = Session(bind=engine)
            all_media = session.query(Files).filter(Files.Id_user == user_id).all()
            all_size = 0
            for i in all_media:
                all_size += i.Size_audio

            if size + all_size < 1024 * 1024 * 100:  # - 100 Mb
                new_file = Files(
                    Id_user=user_id,
                    Name_sound=data["name"],
                    Path=local_file_path,
                    Size_audio=size,
                )
                session.add(new_file)
                session.commit()
                session.close()

                await message.answer(
                    f"Good job! Your sound has been successfully added! Try sending it to somebody using @MyBotName inline command! ✅😎"
                )
                await state.clear()
            else:
                session.close()
                await message.answer(
                    "Your disk space limit is reached! Try deleting some unused sounds first! You can find list with all your sounds: /list_sounds ❌😢"
                )
                await state.clear()
        except Exception as e:
            await message.answer(
                f"{e}: {data}: Seems like there is no .mp3 file attached! ❌🧐"
            )
            await state.clear()

    @dp.message(Command("delete_sound"))
    async def delete_message(message: types.Message):
        name = expect(message.text)[14:]
        try:
            Session = sessionmaker()
            session = Session(bind=engine)

            user_id = expect(message.from_user).id

            file = (
                session.query(Files)
                .filter(Files.Name_sound == name, Files.Id_user == user_id)
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

    @dp.message(Command("list_sounds"))
    async def sound_list(message: types.Message):
        Session = sessionmaker()
        session = Session(bind=engine)

        user_id = expect(message.from_user).id

        all_media = session.query(Files).filter(Files.Id_user == user_id).all()

        session.close()

        if all_media != []:
            text = "Your sounds are:\n"

            for i in all_media:
                text += (
                    f"📌 {i.Name_sound} -  <b>"
                    + "{:.2f}".format(i.Size_audio / 1024 / 1024)
                    + " Mb</b>\n"
                )
            await message.answer(text, parse_mode="HTML")
        else:
            await message.answer(
                "There are not any sounds in your collection\nFeel free to add ones using /add_sound <sound_name>🧐"
            )

    @dp.inline_query()
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
                file_id = await upload_voice_and_get_link(
                    inline_query.bot, output_file, inline_query.from_user.id
                )
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
        bot = expect(inline_query.bot)
        for i in files:
            voice = types.InlineQueryResultCachedVoice(
                id=str(i.Id),
                title=i.Name_sound,
                voice_file_id=i.Id_audio,
            )
            res.append(voice)
        if inline_query.query == "":
            await bot.answer_inline_query(
                inline_query.id,
                results=res,
                cache_time=1,
                switch_pm_text=f"All sounds:",
                switch_pm_parameter="list_sounds",
                is_personal=False,
                next_offset="",
            )
        if res == []:
            await bot.answer_inline_query(
                inline_query.id,
                results=res,
                cache_time=1,
                switch_pm_text=f"""Didn't find a file assosiated with entered name "{inline_query.query}" in my storage! ❌😲""",
                switch_pm_parameter=f"list_sounds",
                is_personal=False,
                next_offset="",
            )
        else:
            await bot.answer_inline_query(
                inline_query.id,
                results=res,
                cache_time=1,
                switch_pm_text=f"All sounds, that name starts with: {inline_query.query}",
                switch_pm_parameter="list_sounds",
                is_personal=True,
                next_offset="",
            )
