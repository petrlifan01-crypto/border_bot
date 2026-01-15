# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
import random
from database import init_db, get_checkpoints, update_checkpoint

app = FastAPI()

# Підключаємо шаблони
templates = Jinja2Templates(directory="static")

# Модель даних від користувача
class UserReport(BaseModel):
    checkpoint_id: str
    cars_count: int

# Проста "ШІ" логіка прогнозування
def calculate_wait_time(cars: int) -> str:
    # Припустимо, швидкість пропуску 20 авто/год
    hours = cars / 20
    hours = round(hours, 1)
    
    if hours < 1: return "менше 1 год"
    return f"~{hours} год"

@app.on_event("startup")
async def startup():
    await init_db()
    # Запускаємо фонову задачу емуляції змін черг
    asyncio.create_task(simulate_queue_changes())

# Емуляція змін (замість парсингу для тесту)
async def simulate_queue_changes():
    while True:
        await asyncio.sleep(10) # Кожні 10 сек оновлюємо
        checkpoints = await get_checkpoints()
        for cp in checkpoints:
            change = random.randint(-5, 10) # Випадкова зміна
            new_val = max(0, cp['cars_official'] + change)
            await update_checkpoint(cp['id'], official_val=new_val)
            print(f"Update: {cp['name']} -> {new_val} машин")

# API: Отримати список
@app.get("/api/data")
async def get_data():
    raw_data = await get_checkpoints()
    result = []
    for item in raw_data:
        # Пріоритет даним користувачів, якщо вони свіжі (тут спрощено)
        current_cars = item['cars_official'] 
        result.append({
            **item,
            "wait_time": calculate_wait_time(current_cars),
            "status_color": "green" if current_cars < 30 else ("yellow" if current_cars < 80 else "red")
        })
    return result

# API: Прийняти репорт від користувача
@app.post("/api/report")
async def report_queue(report: UserReport):
    await update_checkpoint(report.checkpoint_id, user_val=report.cars_count)
    return {"status": "ok", "message": "Дякуємо за дані!"}

# Frontend entry point
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Запуск сервера на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)