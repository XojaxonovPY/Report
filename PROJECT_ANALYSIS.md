# ReportBot — Loyiha Tahlili va Hujjatlashtirish (Project Analysis)

Ushbu hujjat **ReportBot** loyihasining to'liq arxitekturasi, ma'lumotlar bazasi tuzilishi, bot logikasi, admin paneli, so'nggi yangilanishlar hamda aniqlangan kamchilik va tavsiyalarni o'z ichiga oladi.

---

## 1. Loyiha haqida umumiy ma'lumot (Overview)

**ReportBot** — CS2 (Counter-Strike 2) va boshqa onlayn o'yinlardagi qoida buzarlarni ("buller"lar) ro'yxatga olish, foydalanuvchilardan shikoyatlar (reportlar) va dalillarni (rasm, video, audio, havola) qabul qilish hamda ushbu shikoyatlarni adminlar tomonidan Telegram bot va Web admin panel orqali ko'rib chiqish va boshqarish uchun mo'ljallangan tizim.

Tizim uchta asosiy komponentdan iborat:
1. **Foydalanuvchi Telegram Boti**: O'yinchilardan shikoyat va dalillarni yig'ish, ularning shikoyatlari holatini ko'rsatish interfeysi.
2. **Admin Telegram Boti (`control_reports.py`)**: Adminlar uchun bot orqali tushgan shikoyatlarni to'g'ridan-to'g'ri ko'rib chiqish, qabul qilish, rad etish (sababi bilan) va arizachi bilan aloqa qilish interfeysi.
3. **Admin Web Paneli (`admin/app.py`)**: Tizimdagi barcha ma'lumotlarni boshqarish uchun Starlette asosidagi veb-boshqaruv paneli.

---

## 2. Texnologiyalar steki (Tech Stack)

| Komponent | Texnologiya | Izoh |
| :--- | :--- | :--- |
| **Dasturlash tili** | Python 3.10+ (tizimda Python 3.12/3.14) | Asosiy backend tili |
| **Bot Freymvorki** | `aiogram 3.x` | Asinxron Telegram Bot freymvorki |
| **Web / Admin Panel** | `Starlette` + `starlette-admin` | Asinxron Admin web paneli |
| **ORM / Database** | `SQLAlchemy 2.0` + `aiosqlite` | Asinxron ORM va SQLite ma'lumotlar bazasi |
| **Migratsiyalar** | `Alembic` | Baza strukturasini versiyalash |
| **Autentifikatsiya** | `bcrypt` | Admin parollarini xeshlashtirish |
| **Konfiguratsiya** | `python-dotenv` | `.env` faylidan konfiguratsiyani o'qish |
| **Media guruh Middleware** | `aiogram.BaseMiddleware` | Rasmlar albomini to'liq ushlab olish uchun maxsus `MediaGroupMiddleware` |
| **Internatsionalizatsiya** | `pybabel` / `aiogram.utils.i18n` | Ko'p tilli qo'llab-quvvatlash (tayyorgarlik bosqichida) |

---

## 3. Loyiha strukturasi (Directory Structure)

```
ReportBot/
├── admin/                         # Admin web panel moduli
│   ├── app.py                     # Starlette app, Starlette-Admin va ModelView sozlamalari
│   └── provider.py                # Custom AuthProvider (Username & Password login)
├── bot/                           # Telegram bot moduli
│   ├── buttons/                   # Tugmalar generatorlari va middleware'lar
│   │   ├── inline.py              # InlineKeyboard builder
│   │   ├── reply.py               # ReplyKeyboard builder
│   │   └── middleware.py          # Media guruhlarni (album) birlashtiruvchi middleware
│   ├── handlers/                  # Bot handlerlari (yo'naltirgichlar)
│   │   ├── __init__.py            # Routerlarni jamlovchi fayl
│   │   ├── main_handler.py        # /start, navigatsiya va foydalanuvchini ro'yxatdan o'tkazish
│   │   ├── accept_handler.py      # Qoida buzar va shikoyat sababini qabul qilish logikasi
│   │   ├── accept_evidence.py     # Dalillarni (rasm, video, audio, havola) qabul qilish va saqlash
│   │   ├── control_reports.py     # Admin va user report boshqaruvi (qabul qilish, rad etish, tarix)
│   │   └── lang.py                # Tilni o'zgartirish handlerlari (kelgusida foydalanish uchun)
│   ├── dispatcher.py              # Dispatcher (dp) obyekti
│   └── states.py                  # FSM (Finite State Machine) holatlari
├── db/                            # Ma'lumotlar bazasi moduli
│   ├── __init__.py                # Async SQLAlchemy Engine
│   ├── enum.py                    # ReportStatus enum aniqlanishi (pending, acceptance, rejected, in progress)
│   ├── exceptions.py              # Custom DatabaseException va logger
│   ├── models.py                  # SQLAlchemy ORM modellari (User, Buller, Reason, Report)
│   ├── session.py                 # AsyncSessionLocal builder
│   └── utils.py                   # Base model hamda generic CRUD Manager klassi
├── migrations/                    # Alembic migratsiya fayllari
│   ├── env.py                     # Alembic muhit sozlamalari
│   └── versions/                  # Migratsiyalar tarixi
├── utils/                         # Yordamchi modullar va konfiguratsiya
│   ├── env_data.py                # Dotenv ma'lumotlarini yuklash klasslari
│   └── settings.py                # Loyiha yo'llari (Base_dir, Env_path)
├── .env                           # Muhit o'zgaruvchilari (tokenlar, DB_URL, admin login)
├── alembic.ini                    # Alembic konfiguratsiya fayli
├── Makefile                       # Qisqa CLI buyruqlari (migratsiya, admin start, i18n)
├── main.py                        # Botni ishga tushirish kirish nuqtasi
├── requirements.txt               # Loyiha bog'liqliklari (dependencies)
└── sqlite.db                      # SQLite ma'lumotlar bazasi fayli
```

---

## 4. Ma'lumotlar bazasi strukturasi (Database Architecture)

### CRUD Menejer (`db/utils.py`)
Barcha modellar `Model` klassidan voris oladi. `Model` esa `Manager` klassi orqali tayyor asinxron CRUD metodlarga ega:
- `create(**kwargs)`: Yangi yozuv qo'shish (returning orqali yaratilgan obyekt qaytadi).
- `get(**filter_)`: Bitta yozuvni olish (`filter_by`).
- `get_all(order_fields, limit, offset)`: Ro'yxatni olish.
- `get_filter(*filter_, ...)`: Shartlar bo'yicha filterlash (`select.where(*filter_)`).
- `update(filter_, **kwargs)`: Yozuvni yangilash (`update.returning`).
- `delete(filter_)`: Yozuvni o'chirish.
- `stream_all(...)`: Katta ma'lumotlar to'plamini oqim holatida yuklash (`stream_scalars`).

### Modellar (`db/models.py`)

#### 1. `User` (Jadval: `users`)
Foydalanuvchilar (shikoyat qiluvchilar va adminlar) jadvali.
- `user_id`: BIGINT (Primary Key, autoincrement) — Telegram chat ID.
- `username`: String(100), nullable — Telegram username.
- `game_username`: String(100), nullable — CS2 / o'yindagi nikneym.
- `is_admin`: Boolean, default `False` — Adminlik belgisi.
- `report_checks`: Integer, default `0` — Admin tomonidan tekshirilgan reportlar soni.
- `last_report`: DateTime, nullable — Oxirgi report vaqti.
- `created_at`: DateTime — Yaratilgan vaqti.
- **Yordamchi metodlar**:
  - `check_user(data)`: Foydalanuvchini bazadan qidirish, yo'q bo'lsa yaratish, nikneymi o'zgargan bo'lsa yangilash.
  - `check_admin(user_id)`: Berilgan `user_id` admin ekanligini tekshirish (`(is_admin, user)` qaytaradi).

#### 2. `Buller` (Jadval: `bullers`)
Qoida buzarlar jadvali.
- `id`: Integer (Primary Key, autoincrement).
- `game_username`: String(100), index=True, nullable — Qoida buzarning o'yindagi nikneymi.
- `steam_id`: BIGINT, index=True, nullable — Qoida buzarning Steam ID raqami.
- `report_count`: Integer, default `1` — Unga tushgan reportlar soni (har safar yangi reportda `+1` oshadi).
- `created_at`: DateTime.

#### 3. `Reason` (Jadval: `reasons`)
Shikoyat sabablari katalogi.
- `id`: Integer (Primary Key).
- `text`: String(300), nullable — Sabab tavsifi (masalan: "Cheating", "Toxic behavior").
- `created_at`: DateTime.

#### 4. `Report` (Jadval: `reports`)
Shikoyatlar (Reportlar) jadvali.
- `id`: Integer (Primary Key).
- `reporter_id`: FK -> `users.user_id` (CASCADE) — Shikoyat qilgan foydalanuvchi.
- `evidence`: JSON (MutableDict) — Dalillar tuzilmasi:
  - `{"photos": ["file_id_1", "file_id_2"]}`
  - `{"video": "file_id"}`
  - `{"audio": "file_id"}`
  - `{"link": "https://..."}`
- `buller_id`: FK -> `bullers.id` (SET NULL) — Qoida buzar ID.
- `reason_id`: FK -> `reasons.id` (SET NULL), nullable — Oldindan belgilangan shikoyat sababi.
- `assigned_admin_id`: FK -> `users.user_id` (SET NULL), nullable — Biriktirilgan admin ID.
- `comment`: TEXT, nullable — Foydalanuvchi o'z so'zi bilan kiritgan sabab/izoh ("Another ➡️" holatida).
- `reason_rejected`: TEXT, nullable — Rad etilgan bo'lsa, rad etish sababi.
- `status`: Enum (`ReportStatus`: `pending`, `acceptance`, `rejected`, `in progress`), default `pending`.
- `updated_at`: DateTime — Oxirgi tahrirlangan vaqt.
- `created_at`: DateTime.

---

## 5. Telegram Bot Arxitekturasi (`bot/`)

### FSM Holatlari (`bot/states.py`)
- `States.lang`: Til tanlash holati.
- `RegisterState.gama_username`: CS2 nikneymini kiritish holati.
- `AcceptState`:
  - `steam_id`: Qoida buzarning Steam ID raqamini kiritish.
  - `game_username`: Qoida buzarning Game username'ini kiritish.
  - `comment`: Standart sabablar ro'yxatida bo'lmagan shaxsiy sabab/izohni kiritish.
- `EvidenceState`:
  - `photo`: Rasm yoki rasmlar albomini yuborish.
  - `video`: Video yuborish.
  - `audio`: Audio fayl yuborish.
  - `link`: Havola yuborish.
- `RejectState`:
  - `reason`: Admin arizani rad etayotganda rad etish sababini kiritish holati.

---

### Bot Ish Jarayonlari va Handlerlar

#### 1. Foydalanuvchini kutib olish va ro'yxatdan o'tkazish (`main_handler.py`)
- `/start` komandasi berilganda:
  - Agar foydalanuvchi admin bo'lsa (`user.is_admin == True`), maxsus admin menyusi ko'rsatiladi:
    - `["📃 Reports", "📊 Statistic", "📃 My Accept Reports"]`
  - Agar oddiy foydalanuvchi bo'lsa: `RegisterState.gama_username` holatiga o'tkaziladi.
- O'yinchi nikneymi kiritilgach:
  - `User.check_user()` orqali baza bilan sinxronlanadi.
  - Foydalanuvchiga asosiy menyu ko'rsatiladi:
    - `["🟡 Steam ID", "🟠 Game username", "📃 Reports"]`
  - `⬅️ Back` tugmasi ham ushbu bosh sahifaga qaytarish uchun xizmat qiladi.

#### 2. Shikoyat yuborish jarayoni (`accept_handler.py` va `accept_evidence.py`)
1. Foydalanuvchi `🟡 Steam ID` yoki `🟠 Game username` tugmasini bosadi va qoida buzar identifikatorini kiritadi.
2. `Reason` jadvalidagi barcha sabablar Inline tugmalar ko'rinishida chiqariladi + `Another ➡️` tugmasi.
3. Agar foydalanuvchi sababni tanlasa — uning ID'si saqlanadi; agar `Another ➡️` bossa — matnli izoh kiritish so'raladi.
4. Sabab kiritilgach, dalil turini tanlash menyusi chiqadi:
   `["📷 Photo", "📹 Video", "🎙 Audio", "🔗 Link", "⬅️ Back"]`
5. Foydalanuvchi dalilni yuboradi:
   - **Rasm (Photo)**: `MediaGroupMiddleware` bir nechta rasmli albomni bitta ro'yxat qilib yig'ib beradi. Yakka yoki ko'p rasm `evidence: {"photos": [...]}` formatida saqlanadi.
   - **Video**: `{"video": file_id}`
   - **Audio**: `{"audio": file_id}`
   - **Havola**: `{"link": url}`
6. `report_creator` funksiyasi orqali:
   - `Buller` mavjud bo'lsa `report_count += 1` qilinadi, bo'lmasa yangisi ochiladi.
   - `Report` jadvaliga `PENDING` statusida yozuv qo'shiladi.
   - Foydalanuvchiga `"Arizangiz qabul qilindi"` xabari chiqadi.

#### 3. Admin va Foydalanuvchi Report Boshqaruvi (`control_reports.py`)
- **`📃 Reports` tugmasi**:
  - **Admin bosganda**: Hali hech bir adminga biriktirilmagan (`assigned_admin_id == None`) va `PENDING` holatidagi arizalar ro'yxatini chiqaradi. Har bir arizaning dalili (rasm albomi, video, audio yoki havola) ko'rsatiladi va tagiga inline tugmalar biriktiriladi:
    - `[Qabul qilish]` (`accept_{admin_id}_{report_id}`)
    - `[Rad Etish]` (`reject_{admin_id}_{report_id}`)
  - **Foydalanuvchi bosganda**: Foydalanuvchi o'zi yuborgan barcha arizalar tarixini (statusi, biriktirilgan admini va dalillari bilan) ko'radi.
- **Admin tomonidan arizani ko'rib chiqish sikli**:
  1. `Qabul qilish` bosilganda: Ariza holati `IN_PROGRESS` ga o'tadi, adminga biriktiriladi va adminga yangi tugmalar chiqadi:
     - `[Yakunlash]` (`finish_{admin_id}_{report_id}`)
     - `[Rad Etish]` (`reject_{admin_id}_{report_id}`)
  2. `Yakunlash` bosilganda: Ariza statusi `ACCEPTANCE` bo'ladi, adminning `report_checks` hisobi 1 taga oshadi va arizachiga bot orqali xabar yuboriladi:
     > *"Sizning #ID idli arizangiz admin tarafidan qabul qilindi"*
  3. `Rad Etish` bosilganda: Admin `RejectState.reason` holatiga o'tadi va rad etish sababini yozadi. Ariza `REJECTED` holatiga o'tadi va foydalanuvchiga rad etish sababi bilan birga xabar yetkaziladi.
- **`📃 My Accept Reports` tugmasi**:
  - Admin o'zi qabul qilgan (`ACCEPTANCE`) yoki hozirda jarayonda bo'lgan (`IN_PROGRESS`) arizalar ro'yxatini ko'rishi mumkin.

---

## 6. Admin Web Paneli (`admin/`)

- `admin/app.py` orqali Starlette ilovasiga `starlette_admin` ulangan.
- Barcha 4 ta model uchun maxsus `ModelView` klasslari moslashtirilgan:
  1. **`UserAdmin`** (`Foydalanuvchilar`): Icon: `fa-solid fa-users`, saralash va qidiruv maydonlari sozlangan. Custom Actionlar: **Admin qilish** (`make_admin`) va **Adminlikni olib tashlash** (`revoke_admin`).
  2. **`ReportAdmin`** (`Shikoyatlar`): Icon: `fa-solid fa-triangle-exclamation`, eng so'nggi shikoyatlar birinchi bo'lib chiqadi. Custom Actionlar: **Qabul qilish** (`accept_reports`), **Rad etish** (`reject_reports`), **Jarayonga o'tkazish** (`in_progress_reports`).
  3. **`BullerAdmin`** (`Qoida buzarlar`): Icon: `fa-solid fa-user-slash`, shikoyat soni (`report_count`) bo'yicha kamayish tartibida saralanadi.
  4. **`ReasonAdmin`** (`Shikoyat sabablari`): Icon: `fa-solid fa-list-check`, sabablar matni bo'yicha qidiruv sozlangan.
- `admin/provider.py` orqali `UsernameAndPasswordProvider` tayyorlangan bo'lib, u `.env`dagi `ADMIN_USERNAME` va `ADMIN_PASSWORD` (bcrypt bilan xeshlangan) orqali avtorizatsiya qiladi.

---

## 7. Konfiguratsiya va Muhit O'zgaruvchilari (`utils/env_data.py`, `.env`)

Loyiha quyidagi `.env` kalitlaridan foydalanadi:
- `BOT_TOKEN`: Telegram bot tokeni (`aiogram` uchun).
- `DB_URL`: Ma'lumotlar bazasi ulanish stringi (masalan: `sqlite+aiosqlite:///sqlite.db`).
- `ADMIN_USERNAME`: Admin panel foydalanuvchi nomi.
- `ADMIN_PASSWORD`: Admin panel parolini bcrypt bilan xeshlangani.

---

## 8. Ishga tushirish va Buyruqlar (`Makefile`)

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

## 9. Bajarilgan Ishlar, Aniqlangan Kamchiliklar va Tavsiyalar (Status & Roadmap)

### ✅ Bajarilgan va hal qilingan vazifalar:
1. **Dalil qabul qilish to'liq joriy qilindi (`bot/handlers/accept_evidence.py`)**: Rasm, albom, video, audio va havolalar bazaga JSON ko'rinishida saqlanmoqda.
2. **Albomlar bilan ishlash (`bot/buttons/middleware.py`)**: `MediaGroupMiddleware` qo'shildi, media guruhlar to'g'ri qayta ishlanmoqda.
3. **Telegram bot orqali arizalarni to'liq tekshirish sikli (`bot/handlers/control_reports.py`)**: Qabul qilish (`IN_PROGRESS`), yakunlash (`ACCEPTANCE`) va sababi bilan rad etish (`REJECTED`) logikasi yaratildi. Arizachiga xabarnomalar yuborilmoqda.
4. **Admin web panel autentifikatsiyasi to'liq ishladi**: `admin/provider.py` va `admin/app.py` integratsiyasi muvaffaqiyatli yakunlangan.

---

### ⚠️ Aniqlangan kamchiliklar va xatoliklar (Bugs & Code Quality):

1. **`accept_evidence.py` da noto'g'ri havola kiritilganda to'xtamaslik xatosi (Bug)**:
   - 88-89 qatorlarda havola `https://` bilan boshlanmagan taqdirda `"Incorrect link"` xabari beriladi, lekin `return` qo'yilmagan. Natijada noto'g'ri link baribir bazaga yoziladi.
   - Shuningdek, dalil yuborilgach `state.clear()` qilinmagan, bu esa FSM holati to'xtab qolishiga olib kelishi mumkin.

2. **Admin menyusidagi `📊 Statistic` tugmasi**:
   - `main_handler.py` da admin menyusiga `📊 Statistic` qo'shilgan, biroq ushbu tugma uchun hech qanday handler mavjud emas. Bosilganda hech narsa sodir bo'lmaydi.

3. **`main.py` dagi ortiqcha debug kodi**:
   - 33-qatorda `print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()).decode())` qolib ketgan. Bot har safar ishga tushganda terminalga ortiqcha xesh chiqaradi.

4. **Model tiplari nomuvofiqligi (`db/models.py`)**:
   - `Report.reason_rejected: Mapped[bool] = mapped_column(TEXT, nullable=True)` — Python type hint `bool` deb ko'rsatilgan, lekin ustun turi `TEXT` va amalda matn (rad etish sababi) yozilmoqda. `Mapped[str | None]` bo'lishi kerak.
   - `RegisterState.gama_username`: o'rniga to'g'ri imloda `game_username` deb nomlash tavsiya etiladi.

5. **`control_reports.py` da dalillar bo'sh bo'lgan holatdagi xavf**:
   - `match report.evidence:` blokida faqat `photos`, `video`, `audio`, `link` kutilmoqda. Agar dalilsiz ariza bo'lsa yoki boshqa formatda bo'lsa, hech qanday xabar chiqmaydi. `case _:` default shoxchasi kerak.
   - Shuningdek, `report.reporter.username` agar `None` bo'lsa, `@None` ko'rinishida chiqadi.

---

### 🚀 Keyingi reja va takomillashtirish bo'yicha tavsiyalar (TODO):
1. [ ] `📊 Statistic` handlerini yaratish (Admin uchun jami arizalar, qabul qilingan/rad etilgan statistikasi, eng ko'p shikoyat tushgan bullerlar top-5).
2. [ ] `accept_evidence.py` dagi link validatsiyasini to'g'rilash va ariza yuborilgandan so'ng `await state.clear()` chaqirish.
3. [ ] `main.py` dan debug print kodini tozalash.
4. [ ] `Report.reason_rejected` type hintini to'g'rilash.
5. [ ] Ko'p tillilik (i18n) tizimini to'liq yoqish va xabarlarni ko'p tilli qilish.
