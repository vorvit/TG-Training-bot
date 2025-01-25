import asyncio
from aiogram import Router, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
import matplotlib.pyplot as plt
import numpy as np
import os
from translate import Translator

from middleware import LoggingMiddleware
from user import User
from states import Form, Food
from utils import CALORIES, calc_water_norm, calc_calories_norm
from client import get_food_info, get_weather
from config_reader import config

router = Router()
router.message.middleware(LoggingMiddleware())
user = User()

async def setup_database():
    await user.initialize()


asyncio.run(setup_database())

# Обработчик команды /start
@router.message(Command('start'))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    help_ = (
        'Доступны команды:\n'
        '/start - Начало работы\n'
        '/set_profile - Заполняет профиль\n'
        '/show_profile - Показывает профиль\n'
        '/log_water <количество> - Сохраняет количество выпитой воды в мл\n'
        '/log_food <название продукта> - Сохраняет количество полученных каллорий\n'
        '/log_workout <тип тренировки> <время (мин)> - Сохраняет тренировку\n'
        '/check_progress - Показывает прогресс'
    )
    if not await user.user_exists(user_id):
        await message.reply(f'Здравствуйте {message.from_user.first_name}. Это бот для тренировок.\n{help_}')
    else:
        await message.reply(f'С возвращением, {message.from_user.first_name}!\n{help_}')


# Обработчик команды /set_profile
@router.message(Command('set_profile'))
async def cmd_set_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Проверяем, существует ли пользователь
    if await user.user_exists(user_id):
        # Предлагаем обновить профиль
        buttons = [
            types.InlineKeyboardButton(text='Да', callback_data='update_profile_yes'),
            types.InlineKeyboardButton(text='Нет', callback_data='update_profile_no')
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        await message.answer('Ваш профиль уже существует. Хотите обновить его?', reply_markup=keyboard)
    else:
        # Если пользователь не зарегистрирован, создаем нового
        await user.create_user(user_id)
        await state.update_data(user_id=user_id)
        await message.answer('Как Вас зовут: ')
        await state.set_state(Form.name)


@router.callback_query(lambda c: c.data in ['update_profile_yes', 'update_profile_no'])
async def process_update_profile_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    
    if callback_query.data == 'update_profile_yes':
        # Пользователь подтвердил обновление данных
        await user.create_user(user_id)
        await state.update_data(user_id=user_id)
        await callback_query.message.answer('Как Вас зовут: ')
        await state.set_state(Form.name)
    elif callback_query.data == 'update_profile_no':
        # Пользователь отказался от обновления данных
        await callback_query.message.answer('Ваш профиль не был изменен.')

    await callback_query.answer()


@router.message(Form.name)
async def select_sex(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await user.update_user(user_id, name=message.text)

    buttons = [[types.KeyboardButton(text='Мужчина')],
               [types.KeyboardButton(text='Женщина')]]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder='Ваш пол?'
    )

    await message.answer('Ваш пол: ', reply_markup=keyboard)
    await state.set_state(Form.sex)


@router.message(Form.sex)
async def select_age(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await user.update_user(user_id, sex=message.text)

    await message.answer('Ваш возраст, полных лет: ', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


@router.message(Form.age)
async def select_city(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        age = int(message.text)
        if age < 0:
            raise ValueError('Введите правильный возраст')
        await user.update_user(user_id, age=age)

        await message.answer('Ваш город: ')
        await state.set_state(Form.city)
    except ValueError:
        await message.answer('Введите правильный возраст')


@router.message(Form.city)
async def select_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await user.update_user(user_id, city=message.text)
    temperature = await get_weather(
        message.text,
        api_key=config.weather_token.get_secret_value())
    await message.answer(f'Сейчас на улице: {temperature} °C')

    await message.answer('Ваш вес, кг: ')
    await state.set_state(Form.weight)


@router.message(Form.weight)
async def select_height(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError('Введите правильный вес')
        await user.update_user(user_id, weight=weight)
    except ValueError:
        await message.answer('Введите правильный вес')

    await message.answer('Ваш рост, см: ')
    await state.set_state(Form.height)


@router.message(Form.height)
async def select_height(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError('Введите правильный рост')
        await user.update_user(user_id, height=height)
    except ValueError:
        await message.answer('Введите правильный рост')

    await message.answer('Время Ваших тренировок за день в минутах: ')
    await state.set_state(Form.activity)


@router.message(Form.activity)
async def handle_activity_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        activity = float(message.text)
        if activity < 0:
            raise ValueError('Введите верное время тренировки')
        await user.update_user(user_id, activity=activity)
    except ValueError:
        await message.answer('Введите верное время тренировки')
        return

    # Получаем информацию профиля для расчета норм
    profile_data = await user.get_user(user_id)
    water_goal = await calc_water_norm(profile_data)
    calorie_goal = await calc_calories_norm(profile_data)

    # Обновляем цель
    await user.update_user(user_id, water_goal=water_goal, calorie_goal=calorie_goal)

    # Создаем сообщение с рассчитанными нормами
    norms_message = (
        f"Ваши данные записаны!\n\n"
        f"Норма воды: {water_goal} мл\n"
        f"Рассчитанная норма калорий: {calorie_goal} ккал\n"
        f"Вы хотите сохранить эту норму калорий или указать свою?"
    )

    # Инлайн-клавиатура для выбора действия
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сохранить норму', callback_data=f"save_{calorie_goal}")],
        [InlineKeyboardButton(text='Указать свою', callback_data='custom_calorie_input')]
    ])

    await message.answer(norms_message, reply_markup=keyboard)
    await state.clear()


# Обработчик для сохранения рассчитанной нормы калорий
@router.callback_query(lambda c: c.data.startswith('save_'))
async def save_calorie_goal(callback_query: CallbackQuery):
    calorie_goal = int(callback_query.data.split('_')[1])
    await user.update_user(callback_query.from_user.id, calorie_goal=calorie_goal)
    await callback_query.message.answer(f"Норма калорий {calorie_goal} ккал сохранена!")
    await callback_query.answer()


# Обработчик для ввода собственной нормы калорий
@router.callback_query(lambda c: c.data == 'custom_calorie_input')
async def custom_calorie_input(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите вашу норму калорий:")
    await callback_query.answer()
    await state.set_state(Form.custom_calorie)


# Обработчик для получения и установки пользовательской нормы калорий
@router.message(Form.custom_calorie)
async def set_custom_calorie_goal(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        calorie_goal = int(message.text)
        if calorie_goal <= 0:
            raise ValueError("Значение должно быть больше нуля.")
        await user.update_user(user_id, calorie_goal=calorie_goal)
        await message.answer(f"Новая норма калорий {calorie_goal} ккал установлена!")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите правильное число калорий.")


# Обработчик команды /show_profile
@router.message(Command('show_profile'))
async def cmd_show_profile(message: Message):
    user_id = message.from_user.id
    user_data = await user.get_user(user_id)
    if user_data is None:
        await message.answer('Сначала заполните профиль')
        return
    # Функция для безопасного получения числового значения с заменой None
    def safe_round(value, default='значение не задано'):
        return round(value) if value is not None else default

    profile_ = (
        f"Ваш профиль:\n"
        f"Имя: {user_data.get('name', 'значение не задано')} \n"
        f"Пол: {user_data.get('sex', 'значение не задано')} \n"
        f"Возраст: {user_data.get('age', 'значение не задано')} \n"
        f"Город: {user_data.get('city', 'значение не задано')} \n"
        f"Вес: {safe_round(user_data.get('weight'))} кг\n"
        f"Рост: {safe_round(user_data.get('height'))} см\n"
        f"Уровень активности: {user_data.get('activity', 'значение не задано')} мин в день\n"
        f"Цель по калориям: {safe_round(user_data.get('calorie_goal'))} ккал\n"
        f"Цель по выпитой воде: {safe_round(user_data.get('water_goal'))} мл\n"
        f"Выпито воды: {safe_round(user_data.get('logged_water'))} мл\n"
        f"Получено калорий: {safe_round(user_data.get('logged_calories'))} ккал\n"
        f"Потрачено калорий: {safe_round(user_data.get('burned_calories'))} ккал"
    )
    await message.answer(profile_)


# Обработчик команды /log_water
@router.message(Command('log_water'))
async def cmd_log_water(message: Message):
    user_id = message.from_user.id
    user_data = await user.get_user(user_id)
    if user_data is None:
        await message.answer('Сначала заполните профиль')
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer('Введите верные данные, например: /log_water 200')
        return
    try:
        water = float(args[1])
        await user.log_water(user_id, water)
        total_water = await user.get_water(user_id)
        water_goal = user_data['water_goal'] - total_water
        if water_goal > 0:
            await message.answer(f'Выпито воды: {round(total_water)} мл. До выполнения нормы: {round(water_goal)} мл.')
        else:
            await message.answer(f'Выпито воды: {round(total_water)} мл. Норма выполнена.')
    except ValueError:
        await message.answer('Введите верные данные, например: /log_water 200')


# Обработчик команды /log_food
@router.message(Command('log_food'))
async def cmd_log_food(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await user.get_user(user_id)
    if user_data is None:
        await message.answer('Сначала заполните профиль')
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer('Введите верные данные, например: /log_food banana')
        return
    # Перевод пользователя ввода на английский
    translator = Translator(to_lang="en", from_lang="ru")
    food_name = ' '.join(args[1:])
    translated_food_name = translator.translate(food_name)
    food_data = await get_food_info(
        translated_food_name,
        app_id=config.nutritionix_app_id.get_secret_value(),
        api_key=config.nutritionix_app_key.get_secret_value())
    if food_data is None:
        await message.answer(f'Для {food_name} нет данных')
        await state.clear()
        return
    calories = food_data['calories']
    await state.update_data(food_calories=calories)
    await message.reply(f'{food_name} - {calories} ккал на 100 г. Сколько грамм Вы съели?')
    await state.set_state(Food.food_calories)


@router.message(Food.food_calories)
async def set_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    try:
        food_weight = int(message.text)
        await state.update_data(food_weight=food_weight)
    except ValueError:
        await message.answer('Введите правильный вес')
        return
    if food_weight < 0:
        await message.answer('Введите правильный вес')
        return
    food_calories = data.get('food_calories')
    if food_weight is None or food_calories is None:
        await message.answer('Не удалось получить данные')
        return
    total_cal = food_calories * food_weight * 0.01
    await user.log_food(user_id, total_cal)
    await message.answer(f'Записано: {round(total_cal)} ккал')
    await state.clear()


# Обработчик команды /log_workout
@router.message(Command('log_workout'))
async def cmd_log_workout(message: Message):
    user_id = message.from_user.id
    user_data = await user.get_user(user_id)

    if user_data is None:
        await message.answer('Сначала заполните профиль')
        return

    args = message.text.split()

    if len(args) != 3:
        await message.reply('Используйте формат: /log_workout <тип тренировки> <длительность в минутах>')
        return
    workout = args[1].lower()
    duration = float(args[2])

    if workout not in CALORIES:
        await message.reply(f"Выберите тренировку: {'\n'.join(CALORIES.keys())}")
        return

    calories = CALORIES[workout] * duration
    water = duration * 500 / 30
    await user.log_water(user_id, water)
    await user.log_workout(user_id, calories)
    await message.answer(
        f'{workout.capitalize()} {duration} минут — {calories} ккал.\n'
        f'Дополнительно: выпейте {round(water)} мл воды.')


# Вспомогательная функция для создания графика
def plot_progress(user_id, logged, goal, label, file_name):
    fig, ax = plt.subplots()
    labels = ['Выполнено', 'Осталось']
    values = [logged, max(0, goal - logged)]

    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#90A4AE', '#B0BEC5'])
    ax.axis('equal')
    plt.title(f"Прогресс по {label}")
    plt.rcParams['font.family'] = 'DejaVu Sans'

    # Сохраняем график
    plot_path = os.path.join(os.getcwd(), f"{user_id}_{file_name}.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path

# Обработчик команды /check_progress
@router.message(Command('check_progress'))
async def cmd_check_progress(message: Message):
    user_id = message.from_user.id
    user_data = await user.get_user(user_id)

    if user_data is None:
        await message.answer('Сначала заполните профиль')
        return

    logged_water = round(user_data.get("logged_water", 0) or 0)
    water_goal = round(user_data.get("water_goal", 0) or 0)
    logged_calories = round(user_data.get("logged_calories", 0) or 0)
    calorie_goal = round(user_data.get('calorie_goal', 0) or 0)
    burned_calories = round(user_data.get("burned_calories", 0) or 0)

    progress_ = (
        f'Ваш прогресс:\n'
        f'Вода:\n'
        f'- Выпито: {logged_water} мл из {water_goal} мл.\n'
        f'- Осталось: {water_goal - logged_water} мл.\n\n'
        f'Калории:\n'
        f'- Потреблено: {logged_calories} ккал из {calorie_goal} ккал.\n'
        f'- Сожжено: {burned_calories} ккал.\n'
        f'- Баланс: {calorie_goal - logged_calories + burned_calories} ккал.\n'
    )

    await message.answer(progress_)

    # Построение графиков прогресса
    water_progress_plot = plot_progress(user_id, logged_water, water_goal, "воде", "water_progress")
    calorie_progress_plot = plot_progress(user_id, logged_calories, calorie_goal, "калориям", "calorie_progress")

    # Отправка графиков
    try:
        if os.path.exists(water_progress_plot):
            await message.answer_photo(FSInputFile(water_progress_plot))
        else:
            await message.answer("Ошибка: файл для отправки не найден.")

        if os.path.exists(calorie_progress_plot):
            await message.answer_photo(FSInputFile(calorie_progress_plot))
        else:
            await message.answer("Ошибка: файл для отправки не найден.")
    except Exception as e:
        await message.answer("Произошла ошибка при отправке фотографий.")
        print(f"Ошибка при отправке фото: {e}")

    # Удаление файлов с графиками после их отправки
    finally:
        if os.path.exists(water_progress_plot):
            os.remove(water_progress_plot)
        if os.path.exists(calorie_progress_plot):
            os.remove(calorie_progress_plot)
