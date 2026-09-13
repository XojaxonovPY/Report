PORT = 8005
HOST = localhost
.PHONY: admin
mig:
	alembic revision --autogenerate -m "Create a baseline migrations"

# Bazani oxirgi versiyagacha yangilash
upg:
	alembic upgrade head

# Bazani boshlang'ich holatga qaytarish
down:
	alembic downgrade base

# Alembic-ni initsializatsiya qilish
create:
	alembic init migrations

# Admin panelni ishga tushirish
admin:
	uvicorn admin.app:app --host $(HOST) --port $(PORT)



#=========================Til uchun ==========================================
extract:
	pybabel extract --input-dirs=. -o locales/messages.pot
init:
	pybabel init -i locales/messages.pot -d locales -D messages -l uz
	pybabel init -i locales/messages.pot -d locales -D messages -l ru

compile:
	pybabel compile -d locales -D messages

update:
	pybabel update -d locales -D messages -i locales/messages.pot
