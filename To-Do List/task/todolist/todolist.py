from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='Task')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


class Todo:
    state = None
    session = None
    task = {}
    main_menu_options = ("1) Today's tasks", "2) Week's tasks", "3) All tasks", "4) Add task", "0) Exit")

    def __init__(self):
        self.db_init()
        self.back_to_menu()

    def db_init(self):
        engine = create_engine('sqlite:///todo.db?check_same_thread=False')
        Base.metadata.create_all(engine)
        session_ = sessionmaker(bind=engine)
        self.session = session_()

    def main_menu(self, user_input=None):
        if self.state == "main menu":
            self.show_menu()
        elif self.state == "choose option":
            if user_input == "1":
                self.show_tasks("today")
            elif user_input == "2":
                self.show_tasks("week")
            elif user_input == "3":
                self.show_tasks("all")
            elif user_input == "4":
                self.new_task(user_input)
            elif user_input == "0":
                self.exit()
        elif self.state in ("task entered", "deadline entered"):
            self.new_task(user_input)

    def show_menu(self):
        for i in self.main_menu_options:
            print(i)
        self.set_state("choose option")

    def new_task(self, user_input=None):
        if self.state not in ("task entered", "deadline entered"):
            print("\nEnter task")
            self.set_state("task entered")
        elif self.state == "task entered":
            self.task["name"] = user_input
            print("Enter deadline")
            self.set_state("deadline entered")
        else:
            self.task["deadline"] = datetime.strptime(user_input, "%Y-%m-%d")
            new_row = Table(task=self.task["name"], deadline=self.task["deadline"])
            self.session.add(new_row)
            self.session.commit()
            print("The task has been added!\n")
            self.back_to_menu()

    def show_tasks(self, time_unit):
        today = datetime.today()
        if time_unit == "today":
            self.show_task("today", today)
        elif time_unit == "week":
            for i in range(7):
                day = today + timedelta(days=i)
                self.show_task("week", day)
        elif time_unit == "all":
            print("\nAll tasks:")
            rows = self.session.query(Table).order_by(Table.deadline).all()
            if len(rows) == 0:
                print("Nothing to do!")
            else:
                i = 1
                for row in rows:
                    print(f"{i}. {row.task}. {row.deadline.strftime('%#d %b')}")
                    i += 1
        print()
        self.back_to_menu()

    def show_task(self, mode, date):
        rows = self.session.query(Table).filter(Table.deadline == date.date()).all()
        header = ""
        if mode == "today":
            header = "Today"
        elif mode == "week":
            header = date.strftime('%A')
        if len(rows) == 0:
            print(f"\n{header} {date.strftime('%#d %b')}:\nNothing to do!")
        else:
            print(f"\n{header} {date.strftime('%#d %b')}:")
            i = 1
            for row in rows:
                print(f"{i}. {row.task}")
                i += 1

    def set_state(self, state):
        self.state = state

    def back_to_menu(self):
        self.state = "show menu"
        self.show_menu()

    def exit(self):
        self.session.close()
        print("\nBye!")
        self.set_state("exiting")


todolist = Todo()
user_input_ = False
first_run = 1
while True:
    if todolist.state == "exiting":
        break
    else:
        if first_run == 1:
            first_run = None
        else:
            user_input_ = input()
        todolist.main_menu(user_input_)
