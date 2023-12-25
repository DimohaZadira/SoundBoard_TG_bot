from aiogram import types
from aiogram import dispatcher
from aiogram.dispatcher import FSMContext
from tg_bot.states import Add_sound_state
import os
from tg_bot.models import sessionmaker, engine, Files


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
        print(file_path)

        Session = sessionmaker()
        session = Session(bind=engine)
        new_file = Files(
            Id_user=message.from_user.id,
            Name_sound=name,
            Path=file_path[file_path.find("/") :],
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


def register_main_handlers(dp: dispatcher):
    dp.register_message_handler(start_handler, text="/start")
    dp.register_message_handler(add_sound_handler, commands=["add_sound"])
    dp.register_message_handler(delete_message, commands=["delete_sound"], state="*")
    dp.register_message_handler(
        get_audio, content_types=types.ContentType.ANY, state=Add_sound_state.add
    )
    # dp.on(types.Document, get_audio)
