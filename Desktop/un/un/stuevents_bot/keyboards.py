from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню (кнопки внизу экрана)
def main_menu():
    buttons = [
        [KeyboardButton(text="🎪 Выбор мероприятия")],
        [KeyboardButton(text="📸 Прошедшие мероприятия")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Кнопка "Назад в меню" (тоже внизу экрана)
def back_to_main_menu():
    button = [KeyboardButton(text="🏠 Назад в меню")]
    return ReplyKeyboardMarkup(keyboard=[button], resize_keyboard=True)

# Кнопка для конкретного мероприятия (inline)
def event_buttons(event_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить билет", callback_data=f"buy_{event_id}")]
    ])
    return keyboard