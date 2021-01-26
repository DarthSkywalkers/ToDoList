from datetime import datetime

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
    main_menu_options = ["1) Today's tasks", "2) Add task", "0) Exit"]

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
                self.show_tasks()
            elif user_input == "2":
                self.new_task(user_input)
            elif user_input == "0":
                self.exit()
        elif self.state == "enter task":
            self.new_task(user_input)

    def show_menu(self):
        for i in self.main_menu_options:
            print(i)
        self.set_state("choose option")

    def new_task(self, user_input=None):
        if self.state != "enter task":
            print("\nEnter task")
            self.set_state("enter task")
        else:
            new_row = Table(task=user_input)
            self.session.add(new_row)
            self.session.commit()
            print("The task has been added!\n")
            self.back_to_menu()

    def show_tasks(self):
        rows = self.session.query(Table).all()
        if len(rows) == 0:
            print("\nToday:\nNothing to do!")
        else:
            print("\nToday:")
            i = 1
            for row in rows:
                print(f"{i}. {row}")
                i += 1
        print()
        self.back_to_menu()

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
