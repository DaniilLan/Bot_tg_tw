import asyncio
import random
from telethon import TelegramClient, events

# Определение учетных данных API и имен сессий для двух ботов Telegram
api_id_1 = 22269966
api_hash_1 = '507a1cc92759a4e75263263ee5ac1e9e'
session_name_1 = 'assistant_bot1'
bot_token_1 = '7779869736:AAF-OEkppmp2cy1CVGRzBswD98pXTzMvqsA'

api_id_2 = 22269966
api_hash_2 = '507a1cc92759a4e75263263ee5ac1e9e'
session_name_2 = 'assistant_bot2'
bot_token_2 = '7296691653:AAGM7hn0C0vlG9_2tYR6-1BS6x1sfHvRrTc'

# Создание двух клиентов Telegram
client1 = TelegramClient(session_name_1, api_id_1, api_hash_1).start(bot_token=bot_token_1)
client2 = TelegramClient(session_name_2, api_id_2, api_hash_2).start(bot_token=bot_token_2)

# Списки комплектующих и моделей
components = {
    "Видеокарта": [
        "NVIDIA GeForce RTX 3080",
        "AMD Radeon RX 6800 XT",
        "NVIDIA GeForce RTX 3070",
        "AMD Radeon RX 6700 XT",
        "NVIDIA GeForce GTX 1660 Super",
        "NVIDIA GeForce RTX 3090",
        "AMD Radeon RX 580",
        "NVIDIA GeForce RTX 2060",
        "AMD Radeon RX 5700",
        "NVIDIA GeForce GT 1030",
        "NVIDIA GeForce RTX 4080",
        "AMD Radeon RX 6950 XT",
        "NVIDIA GeForce RTX 3060 Ti",
        "AMD Radeon RX 5600 XT",
        "NVIDIA GeForce GTX 1650",
        "NVIDIA GeForce RTX 4070 Ti",
        "AMD Radeon RX 6700",
        "NVIDIA GeForce GTX 1080 Ti",
        "AMD Radeon R9 390X",
        "NVIDIA Titan V"
    ],
    "Процессор": [
        "Intel Core i9-12900K",
        "AMD Ryzen 9 5900X",
        "Intel Core i7-12700K",
        "AMD Ryzen 7 5800X",
        "Intel Core i5-12600K",
        "AMD Ryzen 5 5600X",
        "Intel Core i9-11900K",
        "AMD Ryzen 7 3700X",
        "Intel Core i5-10400F",
        "AMD Ryzen 3 3100",
        "Intel Core i3-10100",
        "AMD Ryzen 5 3500",
        "Intel Xeon W-3175X",
        "AMD Ryzen 9 5950X",
        "Intel Core i7-11700K",
        "AMD Athlon 3000G",
        "Intel Core i5-11400",
        "AMD Ryzen 5 4600G",
        "Intel Core i9-10900K",
        "AMD Ryzen 3 3300X"
    ],
    "Материнская плата": [
        "ASUS ROG Strix Z590-E Gaming",
        "MSI MPG B550 Gaming Edge WiFi",
        "Gigabyte AORUS X570 Master",
        "ASRock B450M Steel Legend",
        "ASUS TUF Gaming B550-PLUS",
        "Gigabyte Z490 AORUS Elite",
        "MSI MAG B550 Tomahawk",
        "ASRock Z490 Taichi",
        "ASUS ROG Crosshair VIII Hero",
        "Gigabyte X570 AORUS Ultra",
        "MSI B450M PRO-VDH MAX",
        "ASUS ROG Strix B450-F Gaming",
        "ASRock X570 Phantom Gaming 4",
        "ASUS Prime Z490-A",
        "Gigabyte B550M AORUS PRO",
        "ASRock Z490 Phantom Gaming 4",
        "MSI Z490 Gaming Plus",
        "ASUS ROG Strix Z490-G Gaming",
        "Gigabyte X570 AORUS Pro",
        "ASRock B550 Steel Legend"
    ],
    "Оперативная память": [
        "Corsair Vengeance LPX 16GB DDR4",
        "G.Skill Ripjaws V 16GB DDR4",
        "Kingston HyperX Fury 16GB DDR4",
        "Crucial Ballistix 16GB DDR4",
        "Corsair Dominator Platinum 32GB DDR4",
        "G.Skill Trident Z RGB 32GB DDR4",
        "Corsair Vengeance RGB Pro 32GB DDR4",
        "HyperX Predator 32GB DDR4",
        "Team Group T-Force Delta 16GB DDR4",
        "Kingston Fury Beast 16GB DDR4",
        "Corsair Vengeance LPX 32GB DDR4",
        "G.Skill Ripjaws 32GB DDR4",
        "Crucial Ballistix Max 32GB DDR4",
        "Patriot Viper Steel 16GB DDR4",
        "ADATA XPG Gammix D30 16GB DDR4",
        "Team Group T-Force Vulcan Z 16GB DDR4",
        "Corsair Vengeance LPX 8GB DDR4",
        "G.Skill Trident Z 16GB DDR4",
        "Crucial Ballistix 8GB DDR4",
        "Kingston HyperX Impact 16GB DDR4"
    ],
    "Блок питания": [
        "Corsair RM850x",
        "Seasonic Focus GX-850",
        "EVGA SuperNOVA 850 G5",
        "Cooler Master V850 Gold",
        "Thermaltake Toughpower GF1 850W",
        "Be Quiet! Straight Power 11 850W",
        "Corsair TX850M",
        "Seasonic Prime 850W",
        "EVGA BQ 850W",
        "Cooler Master MWE Gold 850W",
        "Thermaltake Toughpower 750W",
        "Corsair SF750",
        "Fractal Design Ion+ 760W",
        "FSP Hydro G 850W",
        "Zalman ZM750-GT",
        "Gigabyte P850W",
        "Super Flower Leadex III 850W",
        "Thermaltake Smart Pro RGB 750W",
        "Antec HCG750",
        "Cooler Master MWE Bronze 750W"
    ],
    "Кулер": [
        "Noctua NH-D15",
        "be quiet! Dark Rock Pro 4",
        "Cooler Master Hyper 212 EVO",
        "Cryorig H7",
        "NZXT Kraken X63",
        "Thermalright Dark Rock 4",
        "ARCTIC Freezer 34 eSports DUO",
        "Corsair H100i RGB Platinum",
        "Deepcool Gammaxx 400",
        "Scythe Mugen 5 Rev.B",
        "be quiet! Pure Rock 2",
        "Cooler Master MasterLiquid ML240L",
        "Noctua NH-U12S",
        "Cryorig H5 Universal",
        "NZXT Kraken Z63",
        "Arctic Liquid Freezer II 240",
        "Thermaltake Water 3.0 240 ARGB",
        "ID-COOLING IS-40X",
        "Enermax ETS-T50 AXE",
        "Deepcool GAMMAXX 400 V2"
    ]
}

# Переменная для отслеживания последнего отправленного комплектующего
last_component = None

@client1.on(events.NewMessage)
async def handler1(event):
    global last_component
    # Генерируем случайный комплектующий
    component_name = random.choice(list(components.keys()))

    # Убедимся, что бот не отправляет один и тот же комплектующий дважды подряд
    if component_name != last_component:
        last_component = component_name
        await client2.send_message(event.chat_id, f"Какой у вас {component_name}?")

@client2.on(events.NewMessage)
async def handler2(event):
    # Если сообщение содержит название комплектующего, отправляем случайную модель
    for component_name in components.keys():
        if component_name in event.raw_text:
            model = random.choice(components[component_name])
            await client1.send_message(event.chat_id, f"Модель {component_name}: {model}")
            break

# Запускаем клиенты
loop = asyncio.get_event_loop()
loop.run_until_complete(client1.run_until_disconnected())
loop.run_until_complete(client2.run_until_disconnected())
