from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
import httpx # Для запитів до реальних сайтів
from database import init_db, get_checkpoints, update_checkpoint

app = FastAPI()
templates = Jinja2Templates(directory="static")

class UserReport(BaseModel):
    checkpoint_id: str
    cars_count: int

# === РЕАЛЬНИЙ ПАРСЕР ДАНИХ (єЧерга) ===
async def fetch_echerha_data():
    """
    Беремо дані з офіційного API єЧерги (для вантажівок та автобусів)
    """
    url = "https://echerha.gov.ua/api/website/checkpoints-map"
    
    # Співставлення ID єЧерги з нашими ID в базі
    # Вам треба буде перевірити точні ID на сайті єЧерги, це приклад логіки
    mapping = {
        "Ягодин - Дорогуськ": "yagodyn", # Додайте цей пункт в БД, якщо його немає
        "Краківець - Корчова": "krakivets",
        "Рава-Руська - Гребенне": "rava",
        "Шегині - Медика": "shehyni",
        "Ужгород - Вишнє Нємецьке": "użhorod",
        "Порубне - Сірет": "porubne"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Проходимо по пунктах з єЧерги
                for item in data:
                    name = item.get('title', '')
                    
                    # Шукаємо, якому нашому пункту відповідає ця назва
                    my_id = None
                    for k_name, v_id in mapping.items():
                        if k_name in name:
                            my_id = v_id
                            break
                    
                    if my_id:
                        # Отримуємо черги (структура JSON може змінюватись, це приклад)
                        # Зазвичай там є поля 'live_queue', 'bus_queue' тощо
                        trucks = item.get('attributes', {}).get('truck_live_queue', 0)
                        buses = item.get('attributes', {}).get('bus_live_queue', 0)
                        
                        # Оновлюємо базу реальних даних
                        await update_checkpoint(
                            cp_id=my_id,
                            official_trucks=trucks, # Новий параметр треба додати в update_checkpoint
                            official_buses=buses
                        )
                        print(f"✅ Оновлено {my_id}: Фури {trucks}, Буси {buses}")
            else:
                print(f"Помилка єЧерги: статус {response.status_code}")

    except Exception as e:
        print(f"❌ Помилка парсингу: {e}")

# === ФОНОВЕ ЗАВДАННЯ ===
async def background_updater():
    while True:
        print("🔄 Запуск оновлення даних...")
        
        # 1. Тягнемо офіційні дані (Фури/Буси)
        await fetch_echerha_data()
        
        # 2. Тут могла б бути логіка для легкових (але поки залишаємо на користувачів)
        
        # Чекаємо 5 хвилин (300 сек) перед наступним оновленням
        await asyncio.sleep(300)

@app.on_event("startup")
async def startup():
    await init_db()
    # Запускаємо реальний оновлювач замість симулятора
    asyncio.create_task(background_updater())

@app.get("/api/data")
async def get_data():
    raw_data = await get_checkpoints()
    result = []
    for item in raw_data:
        # Пріоритет даних
        # Легкові: Віримо користувачам (cars_users), якщо вони є, інакше офіційним (cars_official)
        # Фури/Буси: Віримо офіційним (бо ми їх парсимо)
        
        cars = item['cars_users'] if item['cars_users'] > 0 else item['cars_official']
        
        result.append({
            **item,
            # Підміняємо значення на пріоритетні для відображення
            "cars_official": cars, 
            "trucks_official": item['trucks_official'],
            "buses_official": item['buses_official']
        })
    return result

@app.post("/api/report")
async def report_queue(report: UserReport):
    # Тут ми зберігаємо репорт користувача
    # Важливо: в database.py треба оновлювати саме cars_users
    await update_checkpoint(report.checkpoint_id, user_val=report.cars_count)
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})