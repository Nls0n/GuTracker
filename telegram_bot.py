import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, as_section, Bold, Text
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from lk_parser import LKParser
import asyncio
import io
from datetime import datetime

load_dotenv()

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
lk_parser = LKParser()
user_sessions = {}


# ========================
# Состояния FSM
# ========================
class AuthStates(StatesGroup):
    waiting_credentials = State()


# ========================
# Клавиатуры (вынесены отдельно для удобства)
# ========================

def get_start_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ознакомиться")],
        ],
        resize_keyboard=True
    )
    return markup


def get_main_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Авторизоваться"), KeyboardButton(text="Связаться с админом")],
            [KeyboardButton(text="FAQ"), KeyboardButton(text="Личный кабинет")]
        ],
        resize_keyboard=True
    )
    return markup


def get_lk_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Статус моей подписки")],
            [KeyboardButton(text="Моя успеваемость сейчас")],
            [KeyboardButton(text="Авторизоваться")]
        ],
        resize_keyboard=True
    )
    return markup


# ========================
# Фоновые задачи
# ========================
async def monitor_grades(user_id: int, login: str, password: str):
    """Фоновая проверка изменений в оценках"""
    while True:
        try:
            updates = await lk_parser.check_grades_updates(user_id, login, password)
            if updates:
                for diff in updates:
                    await bot.send_message(
                        user_id,
                        f"🔔 Новое изменение:\n{diff['value']}",
                        reply_markup=get_lk_keyboard()
                    )
            await asyncio.sleep(3600)  # Проверка каждые 60 минут
        except Exception as e:
            await bot.send_message(user_id, f"⚠️ Ошибка при проверке оценок: {str(e)}. Необходим релогин")
            await asyncio.sleep(300)  # Пауза при ошибке


# ========================
# Обработчики сообщений
# ========================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""

    hello_msg = """
    Привет, этот бот предназначен для отслеживания оценок в ЛК студента Губкинского университета.
При помощи него ты будешь всегда получать актуальные сведения о любых изменениях в успеваемости из ЛК.
Для начала ознакомься с пользовательским соглашением.
    """
    await message.answer(hello_msg, reply_markup=get_start_keyboard())


@dp.message(F.text == "Ознакомиться")
async def show_agreement(message: Message):
    """Обработчик кнопки 'Ознакомиться'"""
    agreement_msg = """
    Пользование ботом подразумевается платным (чтобы были деньги на хостинг сервера).
До 30.09.2025 бот предполагается как бесплатный, затем планируется переход на полностью платную основу.

Как начать пользоваться?
1. Нажимай на кнопку "Авторизоваться"
2. Вводи данные от своего ЛК в формате: `логин:пароль`

🔒 Ваши данные не сохраняются в БД! 
Для работы бота нужна единоразовая возможность войти в ваш ЛК.
    """
    await message.answer(agreement_msg, reply_markup=get_main_keyboard())


@dp.message(F.text == "Авторизоваться")
async def start_auth(message: Message, state: FSMContext):
    """Начало процесса авторизации"""
    await state.set_state(AuthStates.waiting_credentials)
    await message.answer(
        "🔐 Введите логин и пароль от ЛК в формате: 123456:password",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(AuthStates.waiting_credentials, F.text.regexp(r'^\d+:.+$'))
async def process_credentials(message: Message, state: FSMContext):
    """Обработка введенных учетных данных"""
    try:
        login, password = message.text.split(":")
        user_id = message.from_user.id

        # Проверяем валидность данных (упрощенная версия)
        if len(login) == 6:  # Базовая валидация
            user_sessions[user_id] = {
                'login': login,
                'password': password,
                'task': None
            }

            # Запускаем мониторинг
            user_sessions[user_id]['task'] = asyncio.create_task(
                monitor_grades(user_id, login, password)
            )

            await message.answer(
                "✅ Авторизация успешна! Вы будете получать уведомления.",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer("❌ Неверный формат данных. Логин должен быть 6 цифр, пароль - от 6 символов.")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
    finally:
        await state.clear()

@dp.message(AuthStates.waiting_credentials)
async def wrong_credentials_format(message: Message):
    """Неправильный формат учетных данных"""
    await message.answer("❌ Неверный формат. Введите логин и пароль в формате: 123456:password")


async def send_as_file(user_id: int, data: list):
    """Конвертирует список оценок в текстовый файл"""
    try:
        # Преобразуем список в читаемый текст
        text_data = "📊 Ваши оценки:\n\n"
        for subject in data:
            text_data += f"📚 {subject.get('name', 'Без названия')}\n"
            for grade_type, value in subject.items():
                if grade_type != 'name':
                    text_data += f"  - {grade_type}: {value}\n"
            text_data += "\n"

        # Создаем файл в памяти
        file_buffer = io.BytesIO()
        file_buffer.write(text_data.encode('utf-8'))
        file_buffer.seek(0)

        # Отправляем файл
        await bot.send_document(
            chat_id=user_id,
            document=BufferedInputFile(
                file_buffer.read(),
                filename=f"grades_{datetime.now().strftime('%Y-%m-%d')}.txt"
            ),
            caption="Ваши текущие оценки"
        )
    except Exception as e:
        await bot.send_message(user_id, f"⚠️ Ошибка создания файла: {str(e)}")


@dp.message(F.text == "Моя успеваемость сейчас")
async def current_grades(message: Message):
    """Обработчик кнопки 'Моя успеваемость сейчас'"""
    user_id = message.from_user.id

    if user_id not in user_sessions:
        await message.answer("Сначала авторизуйтесь!")
        return

    try:
        await message.answer("🔄 Загружаю текущие оценки...")

        # Получаем список оценок
        grades_list = await lk_parser.get_current_grades(
            user_sessions[user_id]['login'],
            user_sessions[user_id]['password']
        )

        # Проверяем тип данных
        if not isinstance(grades_list, list):
            raise ValueError("Парсер вернул не список оценок")

        await send_as_file(message.from_user.id, grades_list)

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при загрузке оценок: {str(e)}")


@dp.message(Command("stop"))
async def stop_monitoring(message: Message):
    """Остановка уведомлений"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        if user_sessions[user_id].get('task'):
            user_sessions[user_id]['task'].cancel()
        del user_sessions[user_id]
        await message.answer("🔕 Уведомления отключены.")
    else:
        await message.answer("У вас нет активных сессий.")


@dp.message(F.text == "Связаться с админом")
async def contact_admin(message: Message):
    """Обработчик кнопки 'Связаться с админом'"""
    await message.answer(
        "Связаться с админом можно по [ссылке](t.me/GuTracker_admin)",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(F.text == "Личный кабинет")
async def personal_account(message: Message):
    """Обработчик кнопки 'Личный кабинет'"""
    await message.answer(
        "Что ты хочешь узнать?",
        reply_markup=get_lk_keyboard()
    )
@dp.message(F.text == "FAQ")
async def get_faq(message: Message):
    await message.answer(
        "faq",
        reply_markup=get_lk_keyboard()
    )

@dp.message(F.text == "Статус моей подписки")
async def subscription_status(message: Message):
    """Обработчик кнопки 'Статус моей подписки'"""
    await message.answer("Ваша подписка активна до 30.09.2025")


# ========================
# Запуск бота
# ========================
if __name__ == "__main__":
    # Запуск бота с обработкой KeyboardInterrupt
    async def main():
        await dp.start_polling(bot)


    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
