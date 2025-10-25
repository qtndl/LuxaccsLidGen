from .start import router as start_router
from .in_topic import router as in_topic_router
from .questions import router as questions_router
from .admin_commands import router as admin_router

routers = [admin_router,
           start_router,
           questions_router,
           in_topic_router
           ]

__all__ = ['routers']