import aiosqlite
from datetime import datetime

class User:
    def __init__(self, db_name='user.db'):
        self.db_name = db_name

    async def initialize(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    sex TEXT,
                    age INTEGER,
                    city TEXT,
                    weight REAL,
                    height REAL,
                    activity REAL,
                    water_goal REAL,
                    calorie_goal REAL,
                    logged_water REAL DEFAULT 0,
                    logged_calories REAL DEFAULT 0,
                    burned_calories REAL DEFAULT 0,
                    last_active_date TEXT
                )
            ''')
            await db.commit()

    async def user_exists(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT 1 FROM user WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            # print(f"Checked user_id {user_id}, found: {row is not None}")
            return row is not None

    async def create_user(self, user_id: int):
        if not await self.user_exists(user_id):
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute('''
                    INSERT INTO user (user_id)
                    VALUES (?)
                ''', (user_id,))
                await db.commit()

    async def update_user(self, user_id, **kwargs):
        columns = ', '.join(f'{key} = ?' for key in kwargs)
        values = list(kwargs.values()) + [user_id]
        query = f'UPDATE user SET {columns} WHERE user_id = ?'
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(query, values)
            await db.commit()

    async def get_user(self, user_id: int):
        await self.update_last_active(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
        if result:
            return dict(zip(
                ['user_id', 'name', 'sex', 'age', 'city', 'weight', 'height', 'activity',
                 'water_goal', 'calorie_goal', 'logged_water', 'logged_calories', 'burned_calories'],
                result
            ))
        else:
            return {'error': 'User not found'}

    async def log_water(self, user_id: int, amount: float):
        if amount < 0:
            raise ValueError('Enter correct number')
        await self.update_last_active(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user
                SET logged_water = logged_water + ?
                WHERE user_id = ?
            ''', (amount, user_id))
            await db.commit()

    async def get_water(self, user_id: int):
        await self.update_last_active(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT logged_water FROM user WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def log_food(self, user_id: int, amount: float):
        if amount < 0:
            raise ValueError('Enter correct number')
        await self.update_last_active(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user
                SET logged_calories = logged_calories + ?
                WHERE user_id = ?
            ''', (amount, user_id))
            await db.commit()

    async def log_workout(self, user_id: int, amount: float):
        if amount < 0:
            raise ValueError('Enter correct number')
        await self.update_last_active(user_id)
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user
                SET burned_calories = burned_calories + ?
                WHERE user_id = ?
            ''', (amount, user_id))
            await db.commit()

    async def update_last_active(self, user_id: int):
        today = datetime.now().strftime('%Y-%m-%d')
        # print(f"Today: {today}")
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT last_active_date FROM user WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                # print(f"Last active date from DB: {row[0]}")
                pass
            if row and row[0] != today:
                # print("Resetting data...")
                await db.execute('''
                    UPDATE user
                    SET logged_water = 0,
                        logged_calories = 0,
                        burned_calories = 0,
                        last_active_date = ?
                    WHERE user_id = ?
                ''', (today, user_id))
                await db.commit()
            elif not row:
                # print("Setting last_active_date for a new user.")
                await db.execute('''
                    UPDATE user
                    SET last_active_date = ?
                    WHERE user_id = ?
                ''', (today, user_id))
                await db.commit()
