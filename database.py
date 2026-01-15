# Оновлений шматок для database.py
async def update_checkpoint(cp_id: str, official_val: int = None, user_val: int = None, official_trucks: int = None, official_buses: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        if official_val is not None:
            await db.execute("UPDATE checkpoints SET cars_official = ? WHERE id = ?", (official_val, cp_id))
        
        # Нові поля для парсера
        if official_trucks is not None:
             await db.execute("UPDATE checkpoints SET trucks_official = ? WHERE id = ?", (official_trucks, cp_id))
        if official_buses is not None:
             await db.execute("UPDATE checkpoints SET buses_official = ? WHERE id = ?", (official_buses, cp_id))

        if user_val is not None:
            await db.execute("UPDATE checkpoints SET cars_users = ? WHERE id = ?", (user_val, cp_id))
        
        await db.commit()
