import aiohttp
import asyncio
from config_reader import config

async def get_weather(city, api_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric') as response:
            if response.status == 200:
                weather_data = await response.json()
                temp = weather_data['main']['temp']
                return temp
            else:
                raise Exception(f"Error fetching weather data: {response.status}")


async def get_food_info(product_name, app_id, api_key):
    headers = {
        "x-app-id": app_id,
        "x-app-key": api_key,
        "Content-Type": "application/json"
    }
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    data = {
        "query": product_name,
        "timezone": "US/Eastern"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()  # обработка HTTP ошибок
                data = await response.json()
                foods = data.get('foods', [])

                if foods:
                    food_item = foods[0]  # Берём первый элемент
                    return {
                        'name': food_item.get('food_name', 'Неизвестно'),
                        'calories': food_item['nf_calories']
                    }
                else:
                    print("Продукт не найден.")
                    return None
        except aiohttp.ClientError as e:
            print(f"Ошибка сети: {e}")
            return None
        except ValueError as e:
            print(f"Ошибка обработки данных: {e}")
            return None
