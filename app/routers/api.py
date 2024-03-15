from fastapi import APIRouter

from app.contrib.account.api import api as account_api
from app.contrib.about.api import api as about_api
from app.contrib.config.api import api as config_api
from app.contrib.contact.api import api as contact_api
from app.contrib.media.api import api as media_api
from app.contrib.message.api import api as message_api
from app.contrib.portfolio.api import api as portfolio_api
from app.contrib.post.api import api as post_api
from app.contrib.testimonial.api import api as testimonial_api

api = APIRouter()

api.include_router(account_api, tags=["account", "auth"])
api.include_router(about_api, tags=["about"], prefix="/about")
api.include_router(config_api, tags=["config"], prefix="/config")
api.include_router(contact_api, tags=["contact"], prefix="/contact")
api.include_router(media_api, tags=["media"], prefix="/media")
api.include_router(message_api, tags=["message"], prefix="/message")
api.include_router(portfolio_api, tags=["portfolio"], prefix="/portfolio")
api.include_router(post_api, tags=["post"], prefix="/post")
api.include_router(testimonial_api, tags=["testimonial"], prefix="/testimonial")
