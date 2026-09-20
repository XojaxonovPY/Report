from bot.dispatcher import dp
from bot.handlers.accept_handler import router as accept_router
from bot.handlers.main_handler import router as main_router
from bot.handlers.accept_evidence import router as evidence_router
from bot.handlers.control_reports import router as control_report_router

dp.include_router(main_router)
dp.include_router(accept_router)
dp.include_router(evidence_router)
dp.include_router(control_report_router)