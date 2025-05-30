from fastapi import APIRouter
from app.routes.authorization import router as auth_router
from app.routes.news import router as news_router
from app.routes.attendance import router as attendance_router
from app.routes.payroll import router as payroll_router
from app.routes.status import router as status_router
from app.routes.classification_input import router as classification_router


router = APIRouter()

# Include routes with proper prefixes and tags
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(news_router, prefix="/news", tags=["News"])
router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
router.include_router(payroll_router, prefix="/payroll", tags=["Payroll"])
router.include_router(status_router, prefix="/status", tags=["Status"])
router.include_router(classification_router, prefix="/classification", tags=["Classification"])




