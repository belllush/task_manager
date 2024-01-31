from dataclasses import dataclass
from enum import Enum
from typing import List
import json
from datetime import datetime


class TaskStatus(Enum):
    NEW = "Новая"
    IN_PROGRESS = "Выполняется"
    IN_REVIEW = "Ревью"
    COMPLETED = "Выполнено"
    CANCELED = "Отменено"


@dataclass
class Task:
    # Класс, представляющий задачу с необходимыми атрибутами
    title: str
    description: str
    status: TaskStatus
    created_date: datetime
    status_changed_date: datetime

    def to_dict(self):
        # Метод преобразования задачи в словарь для последующей сериализации в JSON
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_date": self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status_changed_date": self.status_changed_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def from_dict(cls, data):
        # Метод для создания экземпляра задачи из словаря (парсинг из JSON)
        return cls(
            title=data["title"],
            description=data["description"],
            status=TaskStatus(data["status"]),
            created_date=datetime.strptime(data["created_date"], "%Y-%m-%d %H:%M:%S"),
            status_changed_date=datetime.strptime(data["status_changed_date"], "%Y-%m-%d %H:%M:%S"),
        )


class TaskManager:
    # Класс, управляющий задачами и их сохранением/загрузкой
    def __init__(self, tasks: List[Task] = None):
        self.tasks = tasks or []  # Список задач, по умолчанию пустой
        self.history = []  # История действий с задачами

    def add_task(self, task: Task):
        # Метод для добавления новой задачи
        self.tasks.append(task)
        self.history.append(f"Добавлена задача: {task.title}")

    def change_task_status(self, task_title: str, new_status: TaskStatus):
        # Метод для изменения статуса задачи
        for task in self.tasks:
            if task.title == task_title:
                task.status = new_status
                task.status_changed_date = datetime.now()
                self.history.append(f"Статус задачи '{task.title}' изменен на '{new_status.value}'")
                break
        else:
            raise ValueError(f"Задача с названием '{task_title}' не найдена")

    def cancel_task(self, task_title: str):
        # Метод для отмены задачи
        self.change_task_status(task_title, TaskStatus.CANCELED)

    def save_to_file(self, file_path: str):
        # Метод для сохранения состояния задач в файл JSON
        data = {"tasks": [task.to_dict() for task in self.tasks]}
        with open(file_path, "w") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str):
        # Метод для загрузки состояния задач из файла JSON
        with open(file_path, "r") as file:
            data = json.load(file)
        tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return cls(tasks)


if __name__ == "__main__":
    import argparse

    # Инициализация парсера аргументов командной строки
    parser = argparse.ArgumentParser(description="Управление задачами")
    parser.add_argument("file", help="Файл для сохранения/загрузки задач")

    args = parser.parse_args()

    try:
        task_manager = TaskManager.load_from_file(args.file)
    except FileNotFoundError:
        task_manager = TaskManager()

    while True:
        print("\n1. Добавить задачу")
        print("2. Изменить статус задачи")
        print("3. Отменить задачу")
        print("4. Сохранить и выйти")
        print("5. Выйти без сохранения")

        choice = input("Выберите действие (1-5): ")

        if choice == "1":
            # Добавление новой задачи
            title = input("Введите название задачи: ")
            description = input("Введите описание задачи: ")
            task = Task(title=title, description=description, status=TaskStatus.NEW,
                        created_date=datetime.now(), status_changed_date=datetime.now())
            task_manager.add_task(task)
            print(f"Задача '{title}' добавлена.")
        elif choice == "2":
            # Изменение статуса задачи
            title = input("Введите название задачи: ")
            status_str = input("Введите новый статус задачи (NEW, IN_PROGRESS, IN_REVIEW, COMPLETED, CANCELED): ")
            try:
                new_status = TaskStatus[status_str.upper()]
                task_manager.change_task_status(title, new_status)
                print(f"Статус задачи '{title}' изменен на '{new_status.value}'.")
            except KeyError:
                print("Неверный статус.")
        elif choice == "3":
            # Отмена задачи
            title = input("Введите название задачи: ")
            task_manager.cancel_task(title)
            print(f"Задача '{title}' отменена.")
        elif choice == "4":
            # Сохранение и выход
            task_manager.save_to_file(args.file)
            print(f"Состояние задач сохранено в файл '{args.file}'.")
            break
        elif choice == "5":
            # Выход без сохранения
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


#python3 task_manager.py tasks.json

