from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from redis.asyncio import Redis

from app.config import settings

redis = Redis.from_url(settings.redis_url, encoding="utf8", decode_responses=True)


class LampStatus(Enum):
    on = "on"
    off = "off"


class DefaultLamps(Enum):
    lamp1 = "lamp1"
    lamp2 = "lamp2"
    lamp3 = "lamp3"
    lamp4 = "lamp4"


class Lamp(BaseModel):
    name: DefaultLamps
    status: LampStatus


class ArduinoStatus(Enum):
    on = "1"
    off = "0"


class ArduinoLamp(BaseModel):
    d: str
    s: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    for lamp in DefaultLamps.__members__.values():
        print(f"Setting {lamp} to off")
        await redis.set(f"lamps:{lamp}", "off")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/lamps", response_model=list[Lamp])
async def read_lamps():
    lamps = []
    for lamp in DefaultLamps.__members__.values():
        lamps.append(
            Lamp(name=lamp, status=LampStatus(await redis.get(f"lamps:{lamp}")))
        )
    return lamps


@app.get("/ard", response_model=list[ArduinoLamp])
async def read_arduino_lamps():
    lamps = []
    for lamp in DefaultLamps.__members__.values():
        lamp_num = lamp.name.split("lamp")[1]
        lamp_status = await redis.get(f"lamps:{lamp}")
        if lamp_status == "on":
            lamp_status = "1"
        else:
            lamp_status = "0"
        lamps.append(ArduinoLamp(d=lamp_num, s=lamp_status))
    return lamps


@app.post("/lamp", response_model=Lamp)
async def update_lamp(lamp: Lamp):
    print(f"Setting {lamp.name} to {lamp.status.value}")
    await redis.set(f"lamps:{lamp.name}", lamp.status.value)
    return lamp


@app.get("/lamp/{lamp_name}", response_model=Lamp)
async def read_lamp(lamp_name: DefaultLamps):
    status = LampStatus(await redis.get(f"lamps:{lamp_name}"))
    return Lamp(name=lamp_name, status=status)


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
