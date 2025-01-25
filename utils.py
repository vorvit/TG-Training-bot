from user import User
from client import get_weather
from config_reader import config

CALORIES = {
    'аэробика': 9,
    'баскетбол': 10,
    'бег': 10,
    'бокс': 13,
    'велосипед': 8,
    'гребля': 8,
    'йога': 4,
    'кроссфит': 12,
    'лыжи': 9,
    'пилатес': 5,
    'плавание': 7,
    'скалолазание': 10,
    'скейтбординг': 6,
    'танцы': 7,
    'футбол': 11,
    'ходьба': 4,
    'штанга': 8
}

async def calc_water_norm(user):
    '''Расчёт дневной нормы воды'''
    weight = user['weight']
    city = user['city']
    activity = user['activity']

    water_norm = weight * 30 + 500 * (activity / 30)
    try:
        temperature = await get_weather(
            city,
            api_key=config.weather_token.get_secret_value())
        if temperature > 25:
            water_norm += 750
    except:
        pass
    return round(water_norm)


async def calc_calories_norm(user):
    '''Расчет индивидуальной дневной нормы калорий, по формуле Харриса-Бенедикта'''
    weight = user['weight']
    height = user['height']
    age = user['age']
    sex = user['sex']
    activity = user['activity']

    if sex == 'Мужчина':
        calories_norm = 88.36 + 13.4 * weight + 4.8 * height - 5.7 * age
    else:
        calories_norm = 447.6 + 9.2 * weight + 3.1 * height - 4.3 * age
    if activity:
        calories_norm += 9 * activity
    return round(calories_norm)
