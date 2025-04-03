from types import NoneType

from sqlalchemy import create_engine, text
from config import settings
from psycopg2.extras import *


engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=5
)


def insert_request(user_name: str, user_link: str, user_id: int, user_status: str, competition: str, date: DateRange, request: str, status: int, support_id: int):
    try:
        with engine.connect() as conn:
            req = text('INSERT INTO public.requests ("user_name", "user_link", "user_id", "user_status", "competition", date, "request", "status", "support_id") VALUES (:user_name, :user_link, :user_id, :user_status, :competition, :date, :request, :status, :support_id);')
            req = req.bindparams(user_name=user_name, user_link=user_link, user_id=user_id, user_status=user_status, competition=competition, date=date, request=request, status=status, support_id=support_id)
            conn.execute(req)
            req = text("SELECT id FROM public.requests ORDER BY id DESC LIMIT 1;")
            res = conn.execute(req)
            conn.commit()
            return int(res.first()[0])
    except Exception as e:
        return e


def select_req(ids: int):
    with engine.connect() as conn:
        req = text('SELECT "user_name", "user_status", "competition", date, "request", "user_link" FROM public.requests WHERE id=:id;').bindparams(id=ids)
        res = conn.execute(req)
        return res.first()


def select_request_status(ids: int):
    with engine.connect() as conn:
        req = text("SELECT status FROM public.requests WHERE id=:id;").bindparams(id=ids)
        res = conn.execute(req)
        return int(res.first()[0])


def select_request(ids: int):
    with engine.connect() as conn:
        req = text("SELECT request FROM public.requests WHERE id=:id;").bindparams(id=ids)
        res = conn.execute(req)
        return res.first()[0]


def select_karma(ids: int):
    with engine.connect() as conn:
        req = text("SELECT karma FROM public.supports WHERE user_id=:user_id;").bindparams(user_id=ids)
        res = conn.execute(req)
        res = res.first()
        if res is None:
            return 0
        return res[0]


def change_karma(ids: int, new_karma: int):
    with engine.connect() as conn:
        req = text('UPDATE public.supports SET karma=:karma WHERE user_id=:id;').bindparams(karma=new_karma, id=ids)
        res = conn.execute(req)
        conn.commit()
        return res


def change_status(ids: int, status: int):
    with engine.connect() as conn:
        req = text('UPDATE public.requests SET status=:status WHERE id=:id;').bindparams(status=status, id=ids)
        res = conn.execute(req)
        conn.commit()
        return res


def change_support(ids: int, sid: int):
    with engine.connect() as conn:
        req = text('UPDATE public.requests SET support_id=:sid WHERE id=:id;').bindparams(sid=sid, id=ids)
        res = conn.execute(req)
        conn.commit()
        return res
