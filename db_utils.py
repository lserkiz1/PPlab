

from models import Session, Users, calendar, events


def list_users(email=None, first_name=None, last_name=None):
    session = Session()
    filters = []
    if email:
        filters.append(Users.email.like(email))
    if first_name:
        filters.append(Users.email.like(first_name))
    if last_name:
        filters.append(Users.email.like(last_name))
    return session.query(Users).filter(*filters).all()


def list_events(*filters):
    session = Session()
    return (
        session.query(events)
        .join(Users)
        .filter(*filters)
        .all()
    )


def list_events_for_calendar(calendar_id):
    session = Session()
    session.query(calendar).filter_by(uid=calendar_id).one()
    events_from = (
        session.query(events)
        .join(calendar, events.from_calendar_uid == calendar.uid)
        .filter(events.from_calendar_uid == calendar_id)
    )
    events_to = (
        session.query(events)
        .join(calendar, events.to_calendar_uid == calendar.uid)
        .filter(events.to_calendar_uid == calendar_id)
    )
    return (
        events_from.union(events_to)
        .order_by(events.datetime)
        .all()
    )


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry


def get_entry_by_uid(model_class, uid, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(uid=uid, **kwargs).one()


def update_entry(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    return entry


def delete_entry(model_class, uid, *, commit=True, **kwargs):
    session = Session()
    session.query(model_class).filter_by(uid=uid, **kwargs).delete()
    if commit:
        session.commit()
