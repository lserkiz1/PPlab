from models import Session, Users, calendar, events

session = Session()

user = Users(uid=1, email="example@example.com", password=b'', first_name="First", last_name="Last")
calendar_1 = calendar(uid=1, name="My calendar", case=90, owner=user)
calendar_2 = calendar(uid=2, name="My calendar", case=110, owner=user)
event = events(uid=1, from_calendar=calendar_1, to_calendar=calendar_2, text=10)

session.add(user)
session.add(calendar_1)
session.add(calendar_2)
session.add(events)
session.commit()

print(session.query(Users).all())
print(session.query(calendar).all())
print(session.query(events).all())

session.close()