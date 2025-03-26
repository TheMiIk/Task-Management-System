from enum import Enum
import json
from datetime import datetime

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    def __init__(self, level):
        self.level = level

    def to_dict(self):
        return str(self.level)

    def __str__(self):
        return str(self.level)

class Status(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, status_str):
        return cls(status_str)

    def to_dict(self):
        return self.value

class Sequencer:
    sequence = 0

    @classmethod
    def generate_sequence(cls):
        cls.sequence += 1
        return cls.sequence

class Task:
    def __init__(self, id, name, description, priority, status, user):
        self.id = id
        self.name = name
        self.description = description
        self.priority = priority
        self.status = status
        self.user = user

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.id == other.id
        return False

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.priority.name} - {self.status.value}"

    def set_priority(self, priority):
        self.priority = priority

    def set_status(self, status):
        self.status = status

    def to_dict(self):
        priority = self.priority.to_dict() if isinstance(self.priority, Priority) else self.priority
        status = self.status.to_dict() if isinstance(self.status, Status) else self.status
        user_id = self.user.id if isinstance(self.user, User) else self.user
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'priority': priority,
            'status': status,
            'user_id': user_id
        }

class DevTask(Task):
    def __init__(self, id, name, description, priority, status, user, language):
        super().__init__(id, name, description, priority, status, user)
        self.language = language

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["_type"] = "DevTask"
        base_dict["language"] = self.language
        return base_dict

class QATask(Task):
    def __init__(self, id, name, description, priority, status, user, test_type):
        super().__init__(id, name, description, priority, status, user)
        self.test_type = test_type

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["_type"] = "QATask"
        base_dict["test_type"] = self.test_type
        return base_dict

class DocTask(Task):
    def __init__(self, id, name, description, priority, status, user, document):
        super().__init__(id, name, description, priority, status, user)
        self.document = document

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["_type"] = "DocTask"
        base_dict["document"] = self.document
        return base_dict

class Project:
    def __init__(self, id, name, description, deadline=None):
        self.id = id
        self.name = name
        self.description = description
        self.tasks = set()
        self.deadline = (
            datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
        ) if deadline else datetime.now()

    def add_task(self, task: Task):
        self.tasks.add(task)

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.description} (Deadline: {self.deadline})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "tasks": [task.to_dict() for task in self.tasks]
        }


class User:
    def __init__(self, id, name, surname, email):
        self.id = id
        self.name = name
        self.surname = surname
        self.email = email
        self.projects = []

    def create_project(self, name, description, deadline=None):
        project = Project(Sequencer.generate_sequence(), name, description, deadline)
        self.projects.append(project)
        return project

    def remove_project(self, project_id):
        self.projects = [p for p in self.projects if p.id != project_id]

    def __str__(self):
        return f"[{self.id}] {self.name} {self.surname} - {self.email}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "projects": [p.to_dict() for p in self.projects]
        }

class Users:
    users = []

    @classmethod
    def add_user(cls, user: User):
        cls.users.append(user)

    @classmethod
    def remove_user(cls, user_id: int):
        cls.users = [u for u in cls.users if u.id != user_id]

    @classmethod
    def save_data(cls, filename="users.json"):
        with open(filename, "w") as file:
            json.dump([u.to_dict() for u in cls.users], file, indent=4)

    @classmethod
    def load_data(cls, filename="users.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                cls.users = []
                for user_data in data:
                    projects_data = user_data.pop("projects", [])
                    user = User(**user_data)
                    user.projects = []

                    for project_data in projects_data:
                        tasks_data = project_data.pop("tasks", [])
                        project = Project(**project_data)

                        for task_data in tasks_data:
                            task_type = task_data.pop("_type", None)

                            user_id = task_data.pop("user_id", None)
                            task_user = next((u for u in cls.users if u.id == user_id), None)

                            task_data["user"] = task_user

                            if task_type == "DevTask":
                                task = DevTask(**task_data)
                            elif task_type == "QATask":
                                task = QATask(**task_data)
                            elif task_type == "DocTask":
                                task = DocTask(**task_data)
                            else:
                                print(f"Warning: Unknown task type for task {task_data.get('id')}. Skipping.")
                                continue

                            project.add_task(task)

                        user.projects.append(project)
                    cls.users.append(user)
        except FileNotFoundError:
            cls.users = []


def menu():
    while True:
        print("\nTask Management System - Main Menu")
        print("1. Create user")
        print("2. Delete user")
        print("3. Modify user")
        print("4. List users")
        print("5. Create project")
        print("6. Delete project")
        print("7. Modify project")
        print("8. List projects")
        print("9. Create development task")
        print("10. Create quality assurance task")
        print("11. Create documentation task")
        print("12. Delete task")
        print("13. Modify task")
        print("14. List tasks")
        print("15. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_user()
        elif choice == "2":
            delete_user()
        elif choice == "3":
            modify_user()
        elif choice == "4":
            list_users()
        elif choice == "5":
            create_project()
        elif choice == "6":
            delete_project()
        elif choice == "7":
            modify_project()
        elif choice == "8":
            list_projects()
        elif choice == "9":
            create_task("DevTask")
        elif choice == "10":
            create_task("QATask")
        elif choice == "11":
            create_task("DocTask")
        elif choice == "12":
            delete_task()
        elif choice == "13":
            modify_task()
        elif choice == "14":
            list_tasks()
        elif choice == "15":
            Users.save_data()
            print("Exiting the Task Management System. Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

def create_user():
    name = input("Enter name: ")
    surname = input("Enter surname: ")
    email = input("Enter email: ")
    user = User(Sequencer.generate_sequence(), name, surname, email)
    Users.add_user(user)
    print("User created successfully.")

def delete_user():
    user_id = int(input("Enter user ID to delete: "))
    Users.remove_user(user_id)
    print(f"User with ID {user_id} deleted.")

def modify_user():
    user_id = int(input("Enter user ID to modify: "))
    user = next((u for u in Users.users if u.id == user_id), None)
    if user:
        new_name = input(f"Enter new name (current: {user.name}): ")
        new_surname = input(f"Enter new surname (current: {user.surname}): ")
        new_email = input(f"Enter new email (current: {user.email}): ")
        user.name = new_name or user.name
        user.surname = new_surname or user.surname
        user.email = new_email or user.email
        print("User updated successfully.")
    else:
        print("User not found.")

def list_users():
    print("Users:")
    for user in Users.users:
        print(user)

def create_project():
    user_id = int(input("Enter user ID to assign the project: "))
    user = next((u for u in Users.users if u.id == user_id), None)
    if user:
        name = input("Enter project name: ")
        description = input("Enter project description: ")
        deadline = input("Enter project deadline (YYYY-MM-DD): ")
        project = user.create_project(name, description, deadline)
        print(f"Project '{project.name}' created successfully.")
    else:
        print("User not found.")

def delete_project():
    user_id = int(input("Enter user ID: "))
    user = next((u for u in Users.users if u.id == user_id), None)
    if user:
        project_id = int(input("Enter project ID to delete: "))
        user.remove_project(project_id)
        print(f"Project with ID {project_id} deleted.")
    else:
        print("User not found.")


def modify_project():
    project_id = int(input("Enter project ID to modify: "))
    project_to_modify = None

    for user in Users.users:
        for project in user.projects:
            if project.id == project_id:
                project_to_modify = project
                break
        if project_to_modify:
            break

    if project_to_modify:
        print(f"Project found: {project_to_modify.name} - {project_to_modify.description}")

        project_to_modify.name = input(f"New name (current: {project_to_modify.name}): ") or project_to_modify.name
        project_to_modify.description = input(
            f"New description (current: {project_to_modify.description}): ") or project_to_modify.description

        print(f"Current deadline: {project_to_modify.deadline}")
        new_deadline_str = input("Enter new deadline (YYYY-MM-DD): ")
        try:
            new_deadline = datetime.strptime(new_deadline_str, '%Y-%m-%d')
            project_to_modify.deadline = new_deadline
        except ValueError:
            print("Invalid date format. Keeping the current deadline.")

        print(
            f"Project modified: {project_to_modify.name} - {project_to_modify.description} - {project_to_modify.deadline}")
    else:
        print(f"Project with ID {project_id} not found.")


def list_projects():
    print("Projects:")
    for user in Users.users:
        for project in user.projects:
            print(project)

def create_task(task_type):
    user_id = int(input("Enter user ID: "))
    user = next((u for u in Users.users if u.id == user_id), None)
    if user:
        project_id = int(input("Enter project ID to assign the task: "))
        project = next((p for p in user.projects if p.id == project_id), None)
        if project:
            name = input("Enter task name: ")
            description = input("Enter task description: ")
            priority = Priority(int(input("Enter priority (1-LOW, 2-MEDIUM, 3-HIGH, 4-CRITICAL): ")))
            status = Status.NOT_STARTED
            task_id = Sequencer.generate_sequence()

            if task_type == "DevTask":
                language = input("Enter programming language: ")
                task = DevTask(task_id, name, description, priority, status, user, language)
            elif task_type == "QATask":
                test_type = input("Enter test type: ")
                task = QATask(task_id, name, description, priority, status, user, test_type)
            elif task_type == "DocTask":
                document = input("Enter document format: ")
                task = DocTask(task_id, name, description, priority, status, user, document)
            else:
                print("Unknown task type.")
                return

            project.add_task(task)
            print(f"Task '{name}' added to project '{project.name}'.")
        else:
            print("Project not found.")
    else:
        print("User not found.")

def delete_task():
    task_id = int(input("Enter task ID to delete: "))
    task_to_delete = None

    for user in Users.users:
        for project in user.projects:
            for task in project.tasks:
                if task.id == task_id:
                    task_to_delete = task
                    break
            if task_to_delete:
                break
        if task_to_delete:
            break

    if task_to_delete:
        project.tasks.remove(task_to_delete)
        print(f"Task with ID {task_id} has been deleted.")
    else:
        print(f"Task with ID {task_id} not found.")


def modify_task():
    task_id = int(input("Enter task ID to modify: "))
    task_to_modify = None

    for user in Users.users:
        for project in user.projects:
            for task in project.tasks:
                if task.id == task_id:
                    task_to_modify = task
                    break
            if task_to_modify:
                break
        if task_to_modify:
            break

    if task_to_modify:
        print(f"Task found: {task_to_modify.name} - {task_to_modify.description}")

        task_to_modify.name = input(f"New name (current: {task_to_modify.name}): ") or task_to_modify.name
        task_to_modify.description = input(
            f"New description (current: {task_to_modify.description}): ") or task_to_modify.description

        print(f"Current priority: {task_to_modify.priority}")
        new_priority = input("Enter new priority (low, medium, high): ").lower()
        if new_priority == "low":
            task_to_modify.priority = Priority.LOW
        elif new_priority == "medium":
            task_to_modify.priority = Priority.MEDIUM
        elif new_priority == "high":
            task_to_modify.priority = Priority.HIGH
        else:
            print("Invalid priority entered, keeping current priority.")

        print(f"Current status: {task_to_modify.status}")
        new_status = input("Enter new status (not started, in progress, completed): ").lower()
        if new_status in ["not started", "in progress", "completed"]:
            task_to_modify.status = new_status
        else:
            print("Invalid status entered, keeping current status.")

        print(
            f"Task modified: {task_to_modify.name} - {task_to_modify.description} - {task_to_modify.priority} - {task_to_modify.status}")
    else:
        print(f"Task with ID {task_id} not found.")

def list_tasks():
    print("Tasks:")
    for user in Users.users:
        print(f"User: {user.name} {user.surname}")
        for project in user.projects:
            print(f"  Project: {project.name}")
            print(f"  Tasks in set: {project.tasks}")
            if project.tasks:
                for task in project.tasks:
                    print(f"    Task ID: {task.id}, Name: {task.name}, Status: {task.status}, Priority: {task.priority}")
            else:
                print(f"    No tasks found for project {project.name}")



if __name__ == "__main__":
    Users.load_data()
    menu()