# routes.py
from fastapi.responses import HTMLResponse
from fastapi import Query
from fastapi import APIRouter 
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from app.modules.tasks import build_navixy
from app.modules.alerts import get_alerts
from app.modules.trackers import get_trackers
from pydantic import BaseModel
from config import Config
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class AlertInfo(BaseModel):
    dateFrom: str
    dateTo: str
    trackerId: Optional[int] = None


@router.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("bi.html", { "request": {}, "title": "HOla"})

@router.get("/v1/navixy")
def get_info_navixy(days: Optional[int] = None):
    Config.verifyToken()
    return build_navixy(days)

@router.get("/v1/navixy/alerts")
def get_info_navixy_alerts(
    dateFrom: str = Query(..., title="Start Date"),
    dateTo: str = Query(..., title="End Date"),
    trackerId: Optional[int] = Query(None, title="Tracker ID")
):
    Config.verifyToken()
    return get_alerts(dateFrom, dateTo, trackerId)

@router.get("/v1/navixy/trackers")
def get_trackers_list():
    Config.verifyToken()
    return get_trackers()
