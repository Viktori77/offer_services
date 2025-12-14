
all_town_name = {
    "Lipetsk": "Липецк",
    "Gryazi": "Грязи",
    "Eletc": "Елец",
    "Lebedyan": "Лебедянь",
    "Dankov": "Данков",
    "Usman": "Усмань",
    "Chaplygin": "Чаплыгин",
    "Zadonsk": "Задонск",
}

# Модель для всех функций admin (добавить, загрузить, удалить)
all_model_names = {
    "Event": "Мероприятия",
    "Town": "Город",
    "BusSchedule": "Расписание автобусов",
    "EventCheck": "Мероприятия для проверки",
    
}

# Модель для всех пользователей (что они могут посмотреть)
all_model_for_users = {
    "Event": "Мероприятия",
    "BusSchedule": "Расписание автобусов",
}

# Общий словарь для всех разделов
all_sections = {
    "Food": {
        "Cafes": "Кафе",
        "Cafes2": "Рестораны",
        "Cafes3": "Пиццерии",
        "Cafes4": "Роллы/суши",
        "Bakeries": "Пекарни",
        "Confectionery": "Кондитерские",
        "GroceryStores": "Магазины продуктов",
        
    },
    "Services": {
        "Confectioners": "Кондитеры",
        "Taxi": "Такси",
        "AutoRepair": "Ремонт авто",
        "CarRental": "Автомойки",
        "Evakuator": "Спец. техника",
        "ArendaServices": "Аренда спец. техники, авто",
        "BeautySalons": "Салон красоты",
        "ComputerRepair": "Ремонт Компьютеров",
        "ITDevelopers": "ИТ компании",
        "PhotoPrinting": "Фото-печать/ксерокопия",
        "EventDecorations": "Оформление для праздников",
        "Photographers": "Фотографы",
        "PhotoStudio": "Фото-студии",
        "ConstructionCompanies": "Строительные организации",
        "Jurist": "Юр. услуги/Нотариусы",
        "Psyhology": "Психология",
        "RentalServices": "Прокат инвентаря",
        "Tailor": "Швейные услуги",
        "Tourism_agent": "Туристические агенства",
        "ClearHim": "Химчистки",
        
        
    },
    "Stores": {
        "Flowers": "Цветочные салоны",
        "Workshops": "Товыры ручной работы (мастерские)",
        "ClothingStores": "Магазины одежды",
        "ShoeStores": "Магазины обуви",
        "SumkaStores": "Магазины сумок",
        "Stationery": "Канцтовары/Книжные магазины",
        "HouseholdAppliances": "Бытовая техника/электроника/сан.техника",
        "Constraction": "Товары для стройки",
        "Chemist": "Товары для дома",
        "SportingGoods": "Спорт. товары",
        "GardenStores": "Товары для сада",
        'Car': 'Автосалоны',
        "AutoParts": "Авто запчасти",
        "ChildrenStores": "Детские магазины",
        "ShoppingMalls": "Торговые центры",
        "Beekeeper": "Пчеловод",
        "Fabric": "Магазины ткани",
        "Jewelry": "Ювелирные изделия",
        "Kiosk": "Киоски",
        "Newsagent": "Роспечать",
        "Outpost": "Пункты выдачи заказов",
        "Pet": "Зоомагазины",
        "Supermarket": "Супер/гипермаркеты",
        "FixPrice": "Fix Price",
        "VideoGames": "Магазины видео-игр",
        'Hunting': 'Охота, рыбалка',
    },
    "Hospitals": {
        "Hospitals": "Больницы",
        "Pharmacies": "Аптеки",
        "Optics": "Оптика",
        "Massage": "Массаж",
        "Veterinary": "Ветеринарные клиники",
    },
    "Education": {
        "Hight": "ВУЗы",
        "Collages": "Колледжи",
        "Schools": "Общеобразовательные Школы",
        "Kindergartens": "Дет. сады",
        "DrivingSchools": "Автошколы",
        "Libraries": "Библиотеки",
        "ProgresSchools": "Развивающие центры/Дома творчества",
        "Tutors": "Репетиторы",
    },
    "PlayKids": {
        "KidsPlayCenters": "Игровые центры",
        "BowlingAlley": "Бильярд",
        "Parks": "Парки",
        "BaseRest": "Базы отдыха",
        "Sauna": "Бани/сауны",
        "Hotels": "Гостиницы",
        "Animators": "Аниматоры",
        "Cinema": "Театры/кинотеатры",
        "Karaoke": "Караоке/ночные клубы",
        "BeachResort": "Пляжи",
        "IceRink": "Каток",
        "Pitch": "Спортивные площадки",
        "Playground": "Детские площадки",
        
    },
    "Sport": {
        "Pool": "Бассейн",
        "SportScholl": "Спорт. комплексы",
        "SportSection": "Секции/тренировки",
        "Stadium": "Стадионы",
    },
    "Other": {
        "ServicesAdministration": "Административные службы",#Администрация города, районная администрация, суды, ЦК, ПФР, Санпидинстанция, МФЦ, Соц.защита, ЦЕнтр занятости, Водоканал, Горгаз, Электросети, Ростлеком, ЛЭСК, клуб жд, Чайка

        "Factory": "Заводы",
        "Churches": "Храмы",
        "Museum": "Музеи",
        "Roof": "Заправки",
        "Marketplace": "Рынки",
        "Pawnbroker": "Ломбарды",
        "Artwork": "Памятники",
        "Fountain": "Фонтаны",
        "Toilets": "Туалеты",

    },
}


# Список имен моделей для аналогичных таблиц
analog_model_names = {
    # Все разделы
    "Services": "Услуги",
    "Food": "Где покушать?",
    "Stores": "Магазины и торговля",
    "Hospitals": "Здоровье и медицина",
    "Education": "Образование",
    "PlayKids": "Развлечения и досуг",
    "Sport": "О, Спорт! Ты - Мир!",
    "Other": "Другое",
}

# Создаем "перевернутый" словарь
reversed_all_town_name = {v: k for k, v in all_town_name.items()}


# Создаем новый словарь с добавлением суффикса "Reserv" к ключам
analog_model_names_reserv = {key + "Reserv": value for key, value in analog_model_names.items()}

sectionBus={
  # "FromGryaziBusStation": "От автостанции",
  "WithinTheCity": "По городу",
  "OutsideTheCity": "За пределы города",
}



combined_model_names_for_admin = {**all_model_names, **analog_model_names}

combined_model_names_for_users = {**all_model_for_users, **analog_model_names}

combined_model_names_for_settings = {**all_town_name, **all_model_for_users, **analog_model_names}


