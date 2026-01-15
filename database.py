import aiosqlite
import asyncio

DB_NAME = "border.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Створюємо таблицю з НОВИМИ колонками (trucks, buses)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id TEXT PRIMARY KEY,
                name TEXT,
                country TEXT,
                cars_official INTEGER,
                trucks_official INTEGER,
                buses_official INTEGER,
                cars_users INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Перевіряємо, чи база порожня
        cursor = await db.execute("SELECT count(*) FROM checkpoints")
        if (await cursor.fetchone())[0] == 0:
            # Заповнюємо даними для ВСІХ категорій
            initial_data = [
                ("shehyni", "Шегині - Медика", "PL", 120, 450, 2, 0),
                ("krakivets", "Краківець - Корчова", "PL", 45, 800, 10, 0),
                ("rava", "Рава-Руська - Гребенне", "PL", 10, 300, 0, 0),
                ("porubne", "Порубне - Сірет", "RO", 5, 120, 1, 0),
                ("użhorod", "Ужгород - Вишнє Нємецьке", "SK", 30, 200, 5, 0),
            ]
            await db.executemany("""
                INSERT INTO checkpoints 
                (id, name, country, cars_official, trucks_official, buses_official, cars_users) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, initial_data)
            await db.commit()

async def get_checkpoints():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM checkpoints")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def update_checkpoint(cp_id: str, official_val: int = None, user_val: int = None):
    # Ця функція поки що оновлює тільки легкові (для спрощення),
    # але ми її залишаємо, щоб не ламалася логіка репортів
    async with aiosqlite.connect(DB_NAME) as db:
        if official_val is not None:
            await db.execute("UPDATE checkpoints SET cars_official = ? WHERE id = ?", (official_val, cp_id))
        if user_val is not None:
            await db.execute("UPDATE checkpoints SET cars_users = ? WHERE id = ?", (user_val, cp_id))
        await db.commit()