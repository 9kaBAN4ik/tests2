from aiogram import Router, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database import connect_db, add_user, get_user_role, set_user_role,get_referral_bonus,get_user_language
from messages import *  # Импортируем все сообщения
from config import DEFAULT_LANGUAGE, ADMIN_ID
from handlers.menu_handler import back_to_main_menu
router = Router()

# Генерация кнопок для выбора языка
def get_language_markup():
    buttons = [
        InlineKeyboardButton(text="Русский", callback_data="language_ru"),
        InlineKeyboardButton(text="English", callback_data="language_en")
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return markup


@router.callback_query(lambda callback: callback.data.startswith("language_"))
async def process_language_selection(callback: CallbackQuery):
    selected_language = callback.data.split("_")[1]
    if selected_language == "ru":
        await callback.message.answer("Вы выбрали русский язык.")
        # Установите русский язык в настройках пользователя
    elif selected_language == "en":
        await callback.message.answer("You selected English.")
        # Установите английский язык в настройках пользователя

    await callback.answer()  # Закрываем всплывающее уведомление


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user = message.from_user
    user_id = user.id

    # Получаем аргументы команды /start (реферальный код)
    args = message.text.split()[1:]

    # Проверяем, зарегистрирован ли уже пользователь
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            # Если пользователя нет в базе, добавляем его
            await add_user(user_id=user.id, username=user.username, first_name=user.first_name)

            # Формируем сообщение для администраторов
            admin_message = (
                f"👤 Новый пользователь зарегистрировался:\n"
                f"🆔 ID: {user.id}\n"
                f"👤 Имя: {user.first_name or 'Не указано'}\n"
                f"💬 Username: @{user.username or 'Не указан'}"
            )

            # Получаем список администраторов из базы данных
            cursor.execute("SELECT user_id FROM users WHERE role = 'admin'")
            admins = cursor.fetchall()

            # Отправляем уведомление каждому администратору
            for admin in admins:
                admin_id = admin[0]
                try:
                    await message.bot.send_message(chat_id=admin_id, text=admin_message)
                except Exception as e:
                    print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

            # Обработка реферальной ссылки
            if args and args[0].startswith("ref"):
                try:
                    referrer_id = int(args[0].replace("ref", ""))
                    if referrer_id != user_id:
                        referrer_role = await get_user_role(referrer_id) or "user"
                        referral_bonus = get_referral_bonus(event_type="registration", role=referrer_role)

                        # Сохраняем информацию о реферале и начисляем бонус
                        cursor.execute(""" 
                            INSERT INTO referrals (referrer_id, referred_id)
                            VALUES (?, ?)
                        """, (referrer_id, user_id))

                        cursor.execute("""
                            UPDATE users
                            SET balance = balance + ?
                            WHERE user_id = ?
                        """, (referral_bonus, referrer_id))
                        conn.commit()

                        await message.answer(
                            referral_registration_message_ru if DEFAULT_LANGUAGE == 'ru' else referral_registration_message_en)
                    else:
                        await message.answer(
                            referral_error_message_ru if DEFAULT_LANGUAGE == 'ru' else referral_error_message_en)
                except ValueError:
                    await message.answer(
                        invalid_referral_code_message_ru if DEFAULT_LANGUAGE == 'ru' else invalid_referral_code_message_en)
            else:
                await message.answer(
                    registration_success_message_ru if DEFAULT_LANGUAGE == 'ru' else registration_success_message_en)

        else:
            await message.answer(
                already_registered_message_ru if DEFAULT_LANGUAGE == 'ru' else already_registered_message_en)

    # Устанавливаем язык по умолчанию
    await state.update_data(language=DEFAULT_LANGUAGE)

    # Вызов функции меню
    await back_to_main_menu(message, state)


@router.message(lambda message: message.text == "Русский")
async def set_russian(message: Message, state: FSMContext):
    # Обновляем язык в состоянии
    await message.answer("Вы выбрали русский язык.")
    await state.update_data(language="ru")

    # Выполняем дальнейшую логику на основе выбранного языка
    await continue_registration(message, state)


@router.message(lambda message: message.text == "English")
async def set_english(message: Message, state: FSMContext):
    # Обновляем язык в состоянии
    await message.answer("You selected English.")
    await state.update_data(language="en")

    # Выполняем дальнейшую логику на основе выбранного языка
    await continue_registration(message, state)


async def continue_registration(message: Message, state: FSMContext):
    # Получаем язык из состояния
    data = await state.get_data()
    user_language = data.get("language", "en")  # По умолчанию английский

    # Логика, которая зависит от выбранного языка
    if user_language == 'ru':
        await message.answer("Добро пожаловать! Регистрация завершена.")  # Пример сообщения на русском
    else:
        await message.answer("Welcome! Registration is complete.")  # Пример сообщения на английском
