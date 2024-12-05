from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import get_all_products, add_user, is_included
import asyncio

product = get_all_products()


#ВСТАВЬТЕ_СВОЙ_КЛЮЧ_API в строку ниже
api = '_________________________'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.add(button)
kb.add(button2)
kb.add(button3)
kb.add(button4)
# kb.row(KeyboardButton(text='Рассчитать')

kb_in = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
        InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
    ]
]
)
# keyb1 = InlineKeyboardButton(text='Рассчитать норму калорий',callback_data='calories')
# keyb2 = InlineKeyboardButton(text='Формулы расчёта',callback_data='formulas')
# kb_in.add(keyb1,keyb2)
# #kb_in.add(keyb1,keyb2)


kb_in2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton('Product1', callback_data='product_buying'),
        InlineKeyboardButton('Product2', callback_data='product_buying'),
        InlineKeyboardButton('Product3', callback_data='product_buying'),
        InlineKeyboardButton('Product4', callback_data='product_buying')

    ]
]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()



@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(f'Привет, {message.from_user.username}! Мы продаем спортплощадки. Может, ты хочешь '
                         f' рассчитать норму каллорий, узнать о нас побробнее или сделать заказ?' , reply_markup=kb)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Информация о боте!')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    database = get_all_products()
    for i in database:
        await message.answer(f'Продукт: {i[1]}| Описание: {i[2]} | Цена: {i[3] * 100}')
        try:
            with open(f'files/{i[0]}.jpg', 'rb') as img:
                await message.answer_photo(img)
        except FileNotFoundError:
            break
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_in2)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_in)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(ag=message.text)
    await message.answer('Введите свой рост, см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(gr=message.text)
    await message.answer('Введите свой вес, кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(we=message.text)
    data = await state.get_data()
    try:
        cal = int(data['we']) * 10 + 6.25 * int(data['gr']) - 5 * int(data['ag']) + 5
        await message.answer(f'Если вы мужчина, Ваша норма калорий в день составляет {cal}')
        await state.finish()
    except:
        await message.answer('Введены неверные данные! Необходимо вводить только цифры')
        await state.finish()
        await message.answer('Выберите опцию:', reply_markup=kb_in)


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    await state.update_data(user_name=message.text)
    data = await state.get_data(['user_name'])
    if is_included(data['user_name']):
        await message.answer("Пользователь существует, введите другое имя" )
        await RegistrationState.username.set()
    else:
        await state.update_data(users_name=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(user_email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(user_age=message.text)
    data_total = await state.get_data(['user_name', 'user_email', 'user_age'])
    add_user(data_total['user_name'], data_total['user_email'],data_total['user_age'])
    await message.answer('Теперь вы можете перейти к заказу')
    await state.finish()


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
