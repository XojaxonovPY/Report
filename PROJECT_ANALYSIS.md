# ReportBot — Loyiha Tahlili va Hujjatlashtirish (Project Analysis)

Ushbu hujjat **ReportBot** loyihasining to'liq arxitekturasi, ma'lumotlar bazasi tuzilishi, bot logikasi, admin paneli hamda mavjud kamchilik va tavsiyalarni o'z ichiga oladi.

---

## 1. Loyiha haqida umumiy ma'lumot (Overview)

**ReportBot** — CS2 (Counter-Strike 2) va boshqa onlayn o'yinlardagi qoida buzarlarni ("buller"lar) ro'yxatga olish, foydalanuvchilardan shikoyatlar (reportlar) va dalillarni (rasm, video, audio, havola) qabul qilish hamda ushbu shikoyatlarni adminlar tomonidan ko'rib chiqish va boshqarish uchun mo'ljallangan tizim.

Tizim ikkita asosiy qismdan iborat:
1. **Telegram Bot**: Foydalanuvchilar bilan muloqot qilish va shikoyat yuborish interfeysi.
2. **Admin Web Panel**: Shikoyatlar, foydalanuvchilar va sabablarni boshqarish uchun web interfeys.

---

## 2. Texnologiyalar steki (Tech Stack)

| Komponent | Texnologiya | Izoh |
| :--- | :--- | :--- |
| **Dasturlash tili** | Python 3.10+ | Asosiy backend tili |
| **Bot Freymvorki** | `aiogram 3.x` | Asinxron Telegram Bot freymvorki |
| **Web / Admin Panel** | `Starlette` + `starlette-admin` | Asinxron Admin web paneli |
| **ORM / Database** | `SQLAlchemy 2.0` + `aiosqlite` | Asinxron ORM va SQLite ma'lumotlar bazasi |
| **Migratsiyalar** | `Alembic` | Baza strukturasini versiyalash |
| **Autentifikatsiya** | `bcrypt` | Admin parollarini xeshlashtirish |
| **Konfiguratsiya** | `python-dotenv` | `.env` faylidan konfiguratsiyani o'qish |
| **Internatsionalizatsiya** | `pybabel` / `aiogram.utils.i18n` | Ko'p tilli qo'llab-quvvatlash (tayyorgarlik bosqichida) |

---

## 3. Loyiha strukturasi (Directory Structure)

```
ReportBot/
├── admin/                     # Admin panel moduli
│   ├── app.py                 # Starlette app va Starlette-Admin sozlamalari
│   └── provider.py            # Custom AuthProvider (Username & Password login)
├── bot/                       # Telegram bot moduli
│   ├── buttons/               # Tugmalar generatorlari
│   │   ├── inline.py          # InlineKeyboard builder
│   │   └── reply.py           # ReplyKeyboard builder
│   ├── handlers/              # Bot handlerlari (yo'naltirgichlar)
│   │   ├── __init__.py        # Routerni jamlovchi fayl
│   │   ├── accept_handler.py  # Report qabul qilish logikasi
│   │   ├── lang.py            # Tilni o'zgartirish handlerlari
│   │   └── main_handler.py    # /start va foydalanuvchini ro'yxatdan o'tkazish
│   ├── dispatcher.py          # Dispatcher (dp) obyekti
│   └── states.py              # FSM (Finite State Machine) holatlari
├── db/                        # Ma'lumotlar bazasi moduli
│   ├── __init__.py            # Async SQLAlchemy Engine
│   ├── enum.py                # ReportStatus enum aniqlanishi
│   ├── exceptions.py          # Custom DatabaseException va loger
│   ├── models.py              # SQLAlchemy ORM modellari (User, Buller, Reason, Report)
│   ├── session.py             # AsyncSessionLocal builder
│   └── utils.py               # Base model hamda generic CRUD Manager klassi
├── migrations/                # Alembic migratsiya fayllari
│   ├── env.py                 # Alembic muhit sozlamalari
│   └── versions/              # Migratsiyalar tarixi
├── utils/                     # Yordamchi modullar va konfiguratsiya
│   ├── env_data.py            # Dotenv ma'lumotlarini yuklash klasslari
│   └── settings.py            # Loyiha yo'llari (Base_dir, Env_path)
├── .env                       # Muhit o'zgaruvchilari (tokenlar, DB_URL)
├── alembic.ini                # Alembic konfiguratsiya fayli
├── Makefile                   # Qisqa CLI buyruqlari (migratsiya, admin start, i18n)
├── main.py                    # Botni ishga tushirish kirish nuqtasi
├── package.py                 # requirements.txt tozalash skripti
├── requirements.txt           # Loyiha bog'liqliklari (dependencies)
└── sqlite.db                  # SQLite ma'lumotlar bazasi fayli
```

---

## 4. Ma'lumotlar bazasi strukturasi (Database Architecture)

### CRUD Menejer (`db/utils.py`)
Barcha modellar `Model` klassidan voris oladi. `Model` esa o'z navbatida `Manager` klassidan voris olgan holda tayyor asinxron CRUD metodlarga ega:
- `create(**kwargs)`: Yangi yozuv qo'shish.
- `get(**filter_)`: Bitta yozuvni olish.
- `get_all(order_fields, limit, offset)`: Ro'yxatni olish.
- `get_filter(*filter_, ...)`: Shart bo'yicha filterlash.
- `update(filter_, **kwargs)`: Yozuvni yangilash.
- `delete(filter_)`: Yozuvni o'chirish.
- `stream_all(...)`: Katta ma'lumotlar to'plamini oqim holatida yuklash.

### Modellar (`db/models.py`)

#### 1. `User` (Jadval: `users`)
Foydalanuvchilar (shikoyat qiluvchilar va adminlar) jadvali.
- `user_id`: BIGINT (Primary Key) — Telegram chat ID.
- `username`: String(100), nullable — Telegram username.
- `game_username`: String(100), nullable — CS2 / o'yindagi nikneym.
- `is_admin`: Boolean, default `False` — Adminlik belgisi.
- `report_checks`: Integer, default `0` — Tekshirilgan reportlar soni.
- `last_report`: DateTime, nullable — Oxirgi report vaqti.
- `created_at`: DateTime — Yaratilgan vaqti.

#### 2. `Buller` (Jadval: `bullers`)
Qoida buzarlar jadvali.
- `id`: Integer (Primary Key, autoincrement).
- `game_username`: String(100), index=True — Qoida buzarning o'yindagi nikneymi.
- `steam_id`: BIGINT, index=True — Qoida buzarning Steam ID raqami.
- `report_count`: Integer, default `1` — Unga tushgan reportlar soni.
- `created_at`: DateTime.

#### 3. `Reason` (Jadval: `reasons`)
Shikoyat sabablari katalogi.
- `id`: Integer (Primary Key).
- `text`: String(300) — Sabab tavsifi (masalan: "Cheating", "Toxic behavior").
- `created_at`: DateTime.

#### 4. `Report` (Jadval: `reports`)
Shikoyatlar (Reportlar) jadvali.
- `id`: Integer (Primary Key).
- `reporter_id`: FK -> `users.user_id` (CASCADE) — Shikoyat qilgan foydalanuvchi.
- `evidence`: TEXT — Dalil (media fayl ID yoki havola).
- `buller_id`: FK -> `bullers.id` (SET NULL) — Qoida buzar.
- `reason_id`: FK -> `reasons.id` (SET NULL) — Shikoyat sababi.
- `assigned_admin_id`: FK -> `users.user_id` (SET NULL) — Biriktirilgan admin.
- `comment`: TEXT, nullable — Qo'shimcha izoh.
- `reason_rejected`: TEXT, nullable — Rad etish sababi.
- `status`: Enum (`ReportStatus`: `pending`, `acceptance`, `rejected`, `in progress`), default `pending`.
- `updated_at`: DateTime.

---

## 5. Telegram Bot Arxitekturasi (`bot/`)

### FSM Holatlari (`bot/states.py`)
- `States.lang`: Til tanlash holati.
- `RegisterState.gama_username`: CS2 nikneymini kiritish holati.
- `AcceptState`:
  - `steam_id`: Steam ID kiritish.
  - `game_username`: Game username kiritish.
  - `comment`: Ergashgan izoh yozish.

### Handlerlar Logikasi
1. `/start` (`bot/handlers/main_handler.py`):
   - Foydalanuvchiga `RegisterState.gama_username` holatini beradi.
   - Nikneym kiritilgach, `User.check_user()` chaqirilib baza bilan sinxronlanadi va asosiy menyu (`🟡 Steam ID`, `🟠 Game username`, `Reports`) ko'rsatiladi.

2. Shikoyat jarayoni (`bot/handlers/accept_handler.py`):
   - Foydalanuvchi Steam ID yoki Game username ni tanlaydi.
   - `Buller` jadvalidan qoida buzar qidiriladi, yo'q bo'lsa yangisi yaratiladi.
   - `Reason` jadvalidan barcha sabablar Inline tugma shaklida chiqariladi hamda "Another ➡️" opsiyasi beriladi.
   - Sabab tanlangach yoki izoh yozilgach, dalil turini tanlash (Photo, Video, Audio, Link) so'raladi.

---

## 6. Admin Panel (`admin/`)

- `admin/app.py` orqali Starlette ilovasiga `starlette_admin` ulangan.
- Barcha 4 ta model uchun maxsus `ModelView` klasslari moslashtirildi:
  1. **`UserAdmin`** (`Foydalanuvchilar`): Icon: `fa-solid fa-users`, saralash va qidiruv maydonlari sozlangan. Custom Actionlar: **Admin qilish** (`make_admin`) va **Adminlikni olib tashlash** (`revoke_admin`).
  2. **`ReportAdmin`** (`Shikoyatlar`): Icon: `fa-solid fa-triangle-exclamation`, eng so'nggi shikoyatlar birinchi bo'lib chiqadi. Custom Actionlar: **Qabul qilish** (`accept_reports`), **Rad etish** (`reject_reports`), **Jarayonga o'tkazish** (`in_progress_reports`).
  3. **`BullerAdmin`** (`Qoida buzarlar`): Icon: `fa-solid fa-user-slash`, shikoyat soni (`report_count`) bo'yicha kamayish tartibida saralanadi.
  4. **`ReasonAdmin`** (`Shikoyat sabablari`): Icon: `fa-solid fa-list-check`, sabablar matni bo'yicha qidiruv sozlangan.
- `admin/provider.py` orqali `UsernameAndPasswordProvider` tayyorlangan bo'lib, u `.env`dagi `ADMIN_USERNAME` va `ADMIN_PASSWORD` (bcrypt bilan tekshiriladi) orqali avtorizatsiya qiladi.

---

## 7. Konfiguratsiya va Muhit O'zgaruvchilari (`utils/env_data.py`, `.env`)

Loyiha quyidagi `.env` kalitlaridan foydalanadi:
- `BOT_TOKEN`: Telegram bot tokeni (`aiogram` uchun).
- `DB_URL`: Ma'lumotlar bazasi ulanish stringi (masalan: `sqlite+aiosqlite:///sqlite.db`).
- `ADMIN_USERNAME`: Admin panel foydalanuvchi nomi.
- `ADMIN_PASSWORD`: Admin panel parolini bcrypt bilan xeshlangani.

---

## 8. Ishga tushirish va Buyruqlar (`Makefile`)

Loyihada foydali CLI buyruqlari tayyorlangan:

| Buyruq | Vazifasi |
| :--- | :--- |
| `make mig` | Alembic autogenerate migratsiya yaratish |
| `make upg` | Bazani oxirgi versiyagacha yangilash (`alembic upgrade head`) |
| `make down` | Bazani downgrade qilish (`alembic downgrade base`) |
| `make admin` | Uvicorn orqali admin panelni 8005-portda run qilish |
| `make extract`, `init`, `compile` | Pybabel i18n tarjimalari bilan ishlash |

### Botni ishga tushirish:
```bash
python main.py
```

### Admin panelni ishga tushirish:
```bash
make admin
# yoki: uvicorn admin.app:app --host localhost --port 8005
```

---

## 9. Aniqlangan Kamchiliklar va Takomillashtirish Rejasi (Known Issues & TODO)

1. **`AcceptState` dalil qabul qilish handlerlari yetishmaydi**:
   - `accept_handler.py`da `evidence_buttons` ko'rsatiladi, lekin rasm/video/audio/link kelganda uni `Report` jadvaliga saqlaydigan handler hamda adminlarga xabar yuborish logikasi hali yozib tugatilmangan.
2. **Admin Paneldagi Autentifikatsiya**:
   - ilgari `admin/app.py` faylida `# auth_provider=...` izohda bo'lgan hamda `admin/provider.py`da `authenticate` metodi o'rniga `is_authenticated` va `get_admin_user` yozilgani sababli login qilgandan so'ng dashboardga o'tmayotgan edi. Ushbu muammo to'liq tuzatildi (`authenticate` metodi joriy qilindi va app.py da `auth_provider` ulandi).
3. **Imlo xatolari (Code Quality & Naming)**:
   - `RegisterState.gama_username` (o'rniga `game_username`).
   - `Report.reason_rejected`: Python va SQLAlchemy tiplari o'rtasida noaniqlik bor (`Mapped[bool] = mapped_column(TEXT)`).
4. **Ko'p tillilik (i18n)**:
   - `main.py` va `bot/handlers/lang.py` fayllarida `FSMI18nMiddleware` va tarjima logikasi qisman sharhga olingan.
