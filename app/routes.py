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
from datetime import datetime, timedelta


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("bi.html", { "request": {}, "title": "HOla"})

@router.get("/v1/navixy")
def get_info_navixy(days: Optional[int] = None):
    Config.verifyToken()
    return build_navixy(days)

@router.get("/v1/navixy/alerts")
def get_info_navixy_alerts(
    date: Optional[str] = Query(None, title="Date", regex="^\\d{4}-\\d{2}-\\d{2}$"),
    trackerId: Optional[int] = Query(None, title="Tracker ID")
):
    Config.verifyToken()
    if date is None:
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        date = now.strftime('%Y-%m-%d')
        dateFrom = yesterday.strftime('%Y-%m-%d 00:00:00')
        dateTo = now.strftime('%Y-%m-%d %H:%M:%S')
    else:
        dateFrom = f"{date} 00:00:00"
        dateTo = f"{date} 23:59:59"

    print(dateFrom, dateTo)
    return get_alerts(dateFrom, dateTo, trackerId)

@router.get("/v1/navixy/trackers")
def get_trackers_list():
    Config.verifyToken()
    return get_trackers()
