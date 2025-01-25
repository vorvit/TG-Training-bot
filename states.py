from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    name = State()
    sex = State()
    age = State()
    city = State()
    weight = State()
    height = State()
    activity = State()
    calorie_goal = State()
    water_goal = State()
    custom_calorie = State()


class Food(StatesGroup):
    food_calories = State()
    food_weight = State()
    waiting_for_duration = State()
