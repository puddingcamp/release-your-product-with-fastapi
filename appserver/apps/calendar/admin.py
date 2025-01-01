import os
from datetime import datetime

from sqlalchemy import String
import wtforms as wtf
from sqladmin import ModelView
from sqlmodel import Unicode, or_, cast, union
from markupsafe import Markup
from sqlalchemy.sql.expression import Select, select

from appserver.libs.query import exact_match_list_json

from appserver.db import engine
from .models import Booking, BookingFile, Calendar, TimeSlot


class CalendarAdmin(ModelView, model=Calendar):
    category = "캘린더"
    icon = "fa-solid fa-calendar"
    name = "호스트 캘린더"
    name_plural = "호스트 캘린더"
    column_list = [
        Calendar.id,
        Calendar.host,
        Calendar.topics,
        Calendar.google_calendar_id,
        Calendar.created_at,
        Calendar.updated_at,
    ]
    form_columns = [
        Calendar.host,
        Calendar.topics,
        Calendar.description,
        Calendar.google_calendar_id,
    ]
    column_formatters = {
        Calendar.topics: lambda m, r: ", ".join([t for t in m.topics]),
    }
    form_overrides = {
        "google_calendar_id": wtf.EmailField,
    }
    column_searchable_list = [Calendar.topics, Calendar.description]
    column_sortable_list = [
        Calendar.id,
        Calendar.host,
        Calendar.created_at,
        Calendar.updated_at,
    ]
    column_labels = {
        Calendar.id: "ID",
        Calendar.host: "호스트",
        Calendar.topics: "주제",
        Calendar.description: "설명",
        Calendar.google_calendar_id: "Google Calendar ID",
        Calendar.created_at: "생성 일시",
        Calendar.updated_at: "수정 일시",
    }
    column_type_formatters = {
        datetime: lambda v: v.strftime("%Y년 %m월 %d일 %H:%M:%S") if v else "-",
    }
    form_ajax_refs = {
        "host": {
            "fields": ["id", "username", "email"],
            "order_by": "id",
        },
    }

    def search_query(self, stmt: Select, term: str) -> Select:
        # 원래 search_query의 구현에서 따온 부분
        join_expressions = []
        for field in self._search_fields:
            model = self.model
            parts = field.split(".")
            for part in parts[:-1]:
                model = getattr(model, part).mapper.class_
                stmt = stmt.join(model)

            field = getattr(model, parts[-1])
            join_expressions.append(cast(field, String).ilike(f"%{term}%"))

        # JSON 쿼리를 처리하는 부분
        dialect_name = engine.dialect.name # 엔진 이름을 가져옴
        json_expressions = []
        json_expressions.append(
            exact_match_list_json(dialect_name, Calendar.topics, term, Unicode)
        )

        join_query = select(self.model.id).where(or_(*join_expressions))
        json_query = select(self.model.id).where(or_(*json_expressions))

        combined_query = union(join_query, json_query).subquery()

        final_query = select(self.model).join(combined_query, self.model.id == combined_query.c.id)

        return final_query


WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

class TimeSlotAdmin(ModelView, model=TimeSlot):
    category = "캘린더"
    name = "타임슬롯"
    name_plural = "타임슬롯"
    icon = "fa-solid fa-clock"
    column_list = [
        TimeSlot.id,
        TimeSlot.start_time,
        TimeSlot.end_time,
        TimeSlot.weekdays,
        TimeSlot.created_at,
        TimeSlot.updated_at,
    ]
    column_labels = {
        TimeSlot.weekdays: "요일",
        TimeSlot.start_time: "시작 시간",
        TimeSlot.end_time: "종료 시간",
        TimeSlot.created_at: "생성 일시",
        TimeSlot.updated_at: "수정 일시",
    }
    form_columns = [TimeSlot.calendar, TimeSlot.weekdays, TimeSlot.start_time, TimeSlot.end_time]
    column_formatters = {
        TimeSlot.weekdays: lambda m, r: ", ".join([WEEKDAYS[w] for w in m.weekdays]),
    }
    form_ajax_refs = {
        "calendar": {
            "fields": ["id"],
            "order_by": "id",
        },
    }


class BookingAdmin(ModelView, model=Booking):
    category = "캘린더"
    name = "부킹"
    name_plural = "부킹"
    icon = "fa-solid fa-book"
    column_list = [
        Booking.id,
        Booking.time_slot,
        Booking.when,
        Booking.created_at,
        Booking.updated_at,
    ]
    form_columns = [
        Booking.time_slot,
        Booking.when,
        Booking.topic,
        Booking.description,
        Booking.attendance_status,
        Booking.guest,
        Booking.files,
    ]
    form_ajax_refs = {
        "time_slot": {
            "fields": ["id", "start_time", "end_time"],
            "order_by": "id",
        },
        "guest": {
            "fields": ["id", "username", "email"],
            "order_by": "id",
        },
        "files": {
            "fields": ["id"],
            "order_by": "id",
        },
    }


def file_formatter(booking_file: BookingFile, *args, **kwargs) -> Markup:
    file = booking_file.file
    match os.path.splitext(file.name)[1]:    
        case ".jpg" | ".jpeg" | ".png" | ".gif" | ".bmp" | ".tiff" | ".ico" | ".webp":
            return Markup(f'<img src="/{file.path}" style="width: 100px; height: 100px;" />')
        case ".pdf":
            return Markup(f'<i class="fa-solid fa-file-pdf"></i> {file.name}')
        case ".doc" | ".docx":
            return Markup(f'<i class="fa-solid fa-file-word"></i>')
        case ".xls" | ".xlsx":
            return Markup(f'<i class="fa-solid fa-file-excel"></i>')
        case _:
            return Markup(f'<i class="fa-solid fa-file"></i>')


class BookingFileAdmin(ModelView, model=BookingFile):
    category = "캘린더"
    icon = "fa-solid fa-file"
    name = "부킹 첨부파일"
    name_plural = "부킹 첨부파일"
    column_list = [
        BookingFile.id,
        BookingFile.booking,
        BookingFile.file,
    ]
    column_formatters = {
        BookingFile.file: file_formatter,
    }
    form_columns = [BookingFile.booking, BookingFile.file]
    form_ajax_refs = {
        "booking": {
            "fields": ["id"],
            "order_by": "id",
        },
    }
