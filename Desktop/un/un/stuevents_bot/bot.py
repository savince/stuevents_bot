import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN
from keyboards import main_menu, event_buttons, back_to_main_menu
from database import save_guest
from payments import create_payment_url

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_for_fio = State()

# ТВОИ МЕРОПРИЯТИЯ (замени на свои)
EVENTS = [
    {"id": 1, "name": "Концерт 'Рок-весна'", "date": "15.06.2024", "price": 2},
    {"id": 2, "name": "Мастер-класс по фото", "date": "20.06.2024", "price": 4},
    {"id": 3, "name": "Квиз 'Мозгобойня'", "date": "25.06.2024", "price": 3},
]

PAST_EVENTS = [
    {"name": "Концерт 'Джаз-вечер'", "report": "Было круто!", "photos": "https://drive.google.com/..."},
    {"name": "Лекция по маркетингу", "report": "Собрали 50 человек", "photos": "https://drive.google.com/..."},
]

# ===== КОМАНДА /start =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Здравствуй, {message.from_user.first_name}! 👋\n\n"
        "Хочешь на крутое мероприятие? Или посмотреть, как мы отрывались в прошлый раз?",
        reply_markup=main_menu()
    )

# ===== ВЫБОР МЕРОПРИЯТИЯ =====
@dp.message(lambda message: message.text == "🎪 Выбор мероприятия")
async def show_events(message: types.Message):
    # Показываем каждое мероприятие с номером и кнопкой
    for event in EVENTS:
        event_text = (
            f"🎫 **{event['id']}. {event['name']}**\n"
            f"📅 {event['date']}\n"
            f"💰 {event['price']} ₽."
        )
        await message.answer(
            event_text,
            reply_markup=event_buttons(event['id']),
            parse_mode="Markdown"
        )
    
    # Показываем список мероприятий и кнопку "Назад в меню" внизу
    await message.answer(
        text,
        reply_markup=back_to_main_menu(),  # reply-кнопка внизу
        parse_mode="Markdown"
    )
    
    # Для каждого мероприятия добавляем inline-кнопку "Купить билет"
    # Это отдельные сообщения под каждое мероприятие
    for event in EVENTS:
        event_text = f"**{event['name']}**\n{event['date']}\nЦена: {event['price']} руб."
        await message.answer(
            event_text,
            reply_markup=event_buttons(event['id']),  # inline-кнопка "Купить"
            parse_mode="Markdown"
        )

# ===== ДЕТАЛИ МЕРОПРИЯТИЯ =====
@dp.message(lambda message: any(event['name'] in message.text for event in EVENTS))
async def show_event_detail(message: types.Message):
    event = next((e for e in EVENTS if e['name'] in message.text), None)
    if not event:
        return
    
    text = f"**{event['name']}**\n\n📅 {event['date']}\n💰 {event['price']} руб.\n\nОписание мероприятия..."
    await message.answer(text, reply_markup=event_buttons(event['id']), parse_mode="Markdown")

# ===== ПРОШЕДШИЕ МЕРОПРИЯТИЯ =====
@dp.message(lambda message: message.text == "📸 Прошедшие мероприятия")
async def show_past_events(message: types.Message):
    text = "📸 **Прошедшие мероприятия:**\n\n"
    for event in PAST_EVENTS:
        text += f"**{event['name']}**\n{event['report']}\n[Фото]({event['photos']})\n\n"
    await message.answer(text, parse_mode="Markdown")

# ===== КУПИТЬ БИЛЕТ =====
@dp.callback_query(lambda c: c.data and c.data.startswith('buy_'))
async def process_buy(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split('_')[1])
    event = next((e for e in EVENTS if e['id'] == event_id), None)
    
    if not event:
        await callback.answer("Мероприятие не найдено")
        return
    
    await state.update_data(event=event)
    await callback.message.answer("Введите ваше ФИО для оформления билета:")
    await state.set_state(OrderState.waiting_for_fio)
    await callback.answer()

@dp.message(lambda message: message.text == "🏠 Назад в меню")
async def back_to_menu(message: types.Message):
    await cmd_start(message)  # просто вызываем /start

# ===== ВВОД ФИО И ССЫЛКА НА ОПЛАТУ =====
@dp.message(OrderState.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    fio = message.text
    user_data = await state.get_data()
    event = user_data.get('event')
    
    if not event:
        await message.answer("Ошибка, начните заново")
        await state.clear()
        return
    
    # Сохраняем гостя
    username = message.from_user.username or "нет username"
    save_guest(message.from_user.id, username, fio, event['name'])
    
    # Генерируем ссылку на оплату (БЕЗ ТОКЕНОВ!)
    label = f"user_{message.from_user.id}_{event['id']}"
    payment_url, label = create_payment_url(
        amount=event['price'],
        description=f"Билет на {event['name']}",
        label=label
    )
    
    await message.answer(
        f"✅ Спасибо, {fio}!\n\n"
        f"💰 **Сумма:** {event['price']} руб.\n"
        f"🎫 **Мероприятие:** {event['name']}\n\n"
        f"🔗 **Ссылка для оплаты:**\n{payment_url}\n\n"
        f"📌 После оплаты нажмите /confirm, и я пришлю билет"
    )
    await state.clear()

# ===== ПОДТВЕРЖДЕНИЕ ОПЛАТЫ (ВРЕМЕННО) =====
@dp.message(Command("confirm"))
async def confirm_payment(message: types.Message):
    await message.answer(
        "🔍 Спасибо за оплату! Ваш билет:\n\n"
        "https://example.com/qr?code=12345\n\n"
        "(Автоматическую проверку оплаты добавим позже)"
    )

# ===== ЗАПУСК =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())