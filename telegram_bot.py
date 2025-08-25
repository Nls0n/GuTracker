import json
import os
import bcrypt
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
            lk_parser.cursor.execute('''
            UPDATE grades
            SET changed_at = %s
            WHERE telegram_id = %s''', (datetime.now(), user_id))
            updates = await lk_parser.check_grades_updates(user_id, login, password)
            if updates and isinstance(updates, list):
                for diff in updates:
                    await bot.send_message(
                        user_id,
                        f"🔔 Новое изменение:\n{diff}",
                        reply_markup=get_lk_keyboard()
                    )
            else:
                await bot.send_message(
                    user_id,
                    f"Изменений нет",
                    reply_markup=get_lk_keyboard()
                )
            await asyncio.sleep(60)  # Проверка каждые 60 минут
        except Exception as e:
            await bot.send_message(user_id, f"⚠️ Ошибка при проверке оценок: {str(e)}. Необходим релогин")
            await asyncio.sleep(10)  # Пауза при ошибке


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

        # Проверяем валидность данных
        is_correct = await lk_parser.test_credentials(login, password)
        await message.answer('Идет проверка данных, пожалуйста подождите...')
        if len(login) == 6 and is_correct:
            # Безопасная вставка в users
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            lk_parser.cursor.execute('''
                INSERT INTO users (telegram_id, login, password)
                VALUES (%s, %s, %s)
                ON CONFLICT (telegram_id) 
                DO UPDATE SET 
                    login = EXCLUDED.login,
                    password = EXCLUDED.password
            ''', (user_id, login, hashed))

            # Получаем оценки
            grades = await lk_parser.get_current_grades(login, password)

            # Безопасная вставка в grades
            try:
                lk_parser.cursor.execute('''
                UPDATE grades
                SET data = %s
                WHERE telegram_id = %s''', (json.dumps(grades), user_id))
            except:
                lk_parser.cursor.execute('''
                    INSERT INTO grades (telegram_id, data)
                    VALUES (%s, %s)
                ''', (user_id, json.dumps(grades)))
            finally:
                lk_parser.conn.commit()

            # Сохраняем сессию
            user_sessions[user_id] = {
                'login': login,
                'password': hashed,
                'task': asyncio.create_task(
                    monitor_grades(user_id, login, password)
                )
            }

            await message.answer(
                "✅ Авторизация успешна! Вы будете получать уведомления.",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer("❌ Неверные данные. Проверьте корректность логина/пароля")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
        lk_parser.conn.rollback()
    finally:
        await state.clear()

@dp.message(AuthStates.waiting_credentials)
async def wrong_credentials_format(message: Message):
    """Неправильный формат учетных данных"""
    await message.answer("❌ Неверный формат. Введите логин и пароль в формате: 123456:password")


@dp.message(F.text == "Моя успеваемость сейчас")
async def current_grades(message: Message):
    """Обработчик кнопки 'Моя успеваемость сейчас'"""
    user_id = message.from_user.id

    if user_id not in user_sessions:
        await message.answer("🔒 Сначала авторизуйтесь через команду /start")
        return

    try:
        await message.answer("🔄 Загружаю текущие оценки...")

        # Получаем данные из БД
        lk_parser.cursor.execute('''
            SELECT data FROM grades
            WHERE telegram_id = %s
            ORDER BY changed_at DESC
            LIMIT 1
        ''', (user_id,))

        result = lk_parser.cursor.fetchone()[0]
        if not result:
            await message.answer("📭 У вас нет сохраненных оценок")
            return

        grades_data = result  # Получаем JSON данные
        lk_parser.cursor.execute('''
                    SELECT changed_at FROM grades
                    WHERE telegram_id = %s
                    ORDER BY changed_at DESC
                    LIMIT 1
                ''', (user_id,))
        result = lk_parser.cursor.fetchone()[0]
        date_time = result
        if not isinstance(grades_data, list):
            await message.answer("⚠️ Некорректный формат данных оценок")
            return

        # Форматируем оценки для вывода
        formatted_messages = format_grades_data(grades_data)
        print(date_time)
        # Отправляем частями
        for msg in formatted_messages:
            await message.answer(msg, parse_mode="HTML")
        await message.answer(f'Данные актуальны на момент {datetime.strftime(date_time,'%d.%m.%Y - %H:%M')}')

    except Exception as e:
        error_msg = str(e)
        await message.answer(
            f"⚠️ Ошибка при загрузке оценок:\n<code>{error_msg[:1000]}</code>",
            parse_mode="HTML"
        )


def format_grades_data(grades: list) -> list[str]:
    """Форматирует данные оценок для отправки в Telegram"""
    messages = []
    current_msg = ""

    for subject in grades:
        if not isinstance(subject, dict):
            continue

        # Получаем название предмета (первый ключ, который не "Работы")
        subject_name = next(
            (key for key in subject.keys() if key != "Работы"),
            "Неизвестный предмет"
        )
        total_score = subject.get(subject_name, "Нет данных")

        # Форматируем блок предмета
        subject_block = (
            f"<b>════════════════════════════</b>\n"
            f"<b>📚 {subject_name}</b>\n"
            f"<b>🔸 Итого:</b> <code>{str(total_score)}</code>\n\n"
        )

        # Добавляем работы
        works = subject.get("Работы", [])
        if works and isinstance(works, list):
            subject_block += "<b>📝 Работы:</b>\n"
            for i, work in enumerate(works, 1):
                if not isinstance(work, str):
                    continue

                # Очищаем и экранируем текст работы
                work_clean = work.replace('\n', ' ').replace('  ', ' ')

                # Разделяем баллы и описание
                if ' за ' in work_clean:
                    points, desc = work_clean.split(' за ', 1)
                    subject_block += f"{i}. <code>{points.strip()}</code>\n   за {desc.strip()}\n"
                else:
                    subject_block += f"{i}. {work_clean}\n"

        # Проверяем, не превысим ли лимит
        if len(current_msg) + len(subject_block) > 4000:
            messages.append(current_msg)
            current_msg = subject_block
        else:
            current_msg += "\n" + subject_block if current_msg else subject_block

    if current_msg:
        messages.append(current_msg)

    return messages or ["ℹ️ Нет данных для отображения"]


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
