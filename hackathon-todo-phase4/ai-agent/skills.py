"""
Skills Module - Modular Skill-based Agent Architecture
Each skill represents a specific capability that can be invoked by the agent
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pydantic import BaseModel
import httpx
import os
import re


# Skill Base Classes
class SkillInput(BaseModel):
    """Base input for skills"""
    query: str
    context: Dict[str, Any] = {}


class SkillOutput(BaseModel):
    """Base output from skills"""
    success: bool
    message: str
    data: Optional[Any] = None
    suggestions: List[str] = []


@dataclass
class Skill(ABC):
    """Abstract base class for all skills"""
    name: str
    description: str
    keywords: List[str] = field(default_factory=list)
    priority: int = 0  # Higher priority skills are checked first

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """Execute the skill"""
        pass

    def matches(self, query: str) -> bool:
        """Check if this skill matches the query"""
        query_lower = query.lower()
        return any(kw in query_lower for kw in self.keywords)


# Skill Registry
@dataclass
class SkillRegistry:
    """Registry for managing and executing skills"""
    skills: Dict[str, Skill] = field(default_factory=dict)

    def register(self, skill: Skill):
        """Register a skill"""
        self.skills[skill.name] = skill

    def get_matching_skills(self, query: str) -> List[Skill]:
        """Get all skills that match the query, sorted by priority"""
        matching = [s for s in self.skills.values() if s.matches(query)]
        return sorted(matching, key=lambda s: s.priority, reverse=True)

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)

    def list_skills(self) -> List[dict]:
        """List all registered skills"""
        return [
            {
                "name": s.name,
                "description": s.description,
                "keywords": s.keywords
            }
            for s in self.skills.values()
        ]


# Concrete Skills Implementation

@dataclass
class TaskCreationSkill(Skill):
    """Skill for creating new tasks"""
    name: str = "task_creation"
    description: str = "Creates new tasks from natural language input"
    keywords: List[str] = field(default_factory=lambda: [
        "add task", "create task", "new task", "make task", "add a task"
    ])
    priority: int = 10
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        query = input_data.query.lower()

        # Extract task title from query
        match = re.search(r"(?:add|create|new|make)\s+(?:a\s+)?task\s+(.+)", query)
        if not match:
            return SkillOutput(
                success=False,
                message="Please specify a task to add. Format: 'add task <description>'",
                suggestions=["add task buy groceries", "create task finish report"]
            )

        task_title = match.group(1).strip()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/tasks",
                    json={"title": task_title, "description": "", "completed": False},
                    timeout=10.0
                )
                if response.status_code == 200:
                    task = response.json()
                    return SkillOutput(
                        success=True,
                        message=f"Added task: '{task_title}'",
                        data=task
                    )
                else:
                    return SkillOutput(
                        success=False,
                        message=f"Error adding task: {response.text}"
                    )
            except Exception as e:
                return SkillOutput(
                    success=False,
                    message=f"Error connecting to backend: {str(e)}"
                )


@dataclass
class TaskListingSkill(Skill):
    """Skill for listing tasks"""
    name: str = "task_listing"
    description: str = "Lists all tasks with their status"
    keywords: List[str] = field(default_factory=lambda: [
        "list tasks", "show tasks", "my tasks", "get tasks", "all tasks", "view tasks"
    ])
    priority: int = 10
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.backend_url}/tasks", timeout=10.0)
                if response.status_code == 200:
                    tasks = response.json()
                    if not tasks:
                        return SkillOutput(
                            success=True,
                            message="No tasks found. Start by adding a new task!",
                            data=[],
                            suggestions=["add task buy groceries"]
                        )

                    task_list = "**Your Tasks:**\n"
                    for i, task in enumerate(tasks, 1):
                        status = "[DONE]" if task['completed'] else "[TODO]"
                        task_list += f"{i}. {status} **{task['title']}**\n"

                    return SkillOutput(
                        success=True,
                        message=task_list,
                        data=tasks
                    )
                else:
                    return SkillOutput(
                        success=False,
                        message=f"Error retrieving tasks: {response.text}"
                    )
            except Exception as e:
                return SkillOutput(
                    success=False,
                    message=f"Error connecting to backend: {str(e)}"
                )


@dataclass
class TaskDeletionSkill(Skill):
    """Skill for deleting tasks"""
    name: str = "task_deletion"
    description: str = "Deletes tasks by description"
    keywords: List[str] = field(default_factory=lambda: [
        "delete task", "remove task", "delete", "remove"
    ])
    priority: int = 10
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        query = input_data.query.lower()

        match = re.search(r"(?:delete|remove)\s+(?:task\s+)?(.+)", query)
        if not match:
            return SkillOutput(
                success=False,
                message="Please specify which task to delete. Format: 'delete task <description>'",
                suggestions=["delete task grocery shopping"]
            )

        task_desc = match.group(1).strip()

        async with httpx.AsyncClient() as client:
            try:
                # First get all tasks
                tasks_response = await client.get(f"{self.backend_url}/tasks", timeout=10.0)
                if tasks_response.status_code != 200:
                    return SkillOutput(success=False, message="Error retrieving tasks")

                tasks = tasks_response.json()
                task_to_delete = None

                for task in tasks:
                    if task_desc.lower() in task['title'].lower():
                        task_to_delete = task
                        break

                if task_to_delete:
                    delete_response = await client.delete(
                        f"{self.backend_url}/tasks/{task_to_delete['id']}",
                        timeout=10.0
                    )
                    if delete_response.status_code == 200:
                        return SkillOutput(
                            success=True,
                            message=f"Deleted task: '{task_to_delete['title']}'",
                            data=task_to_delete
                        )
                    else:
                        return SkillOutput(
                            success=False,
                            message=f"Error deleting task: {delete_response.text}"
                        )
                else:
                    return SkillOutput(
                        success=False,
                        message=f"Task containing '{task_desc}' not found",
                        suggestions=["list tasks"]
                    )
            except Exception as e:
                return SkillOutput(
                    success=False,
                    message=f"Error: {str(e)}"
                )


@dataclass
class TaskUpdateSkill(Skill):
    """Skill for updating tasks"""
    name: str = "task_update"
    description: str = "Updates task titles and descriptions"
    keywords: List[str] = field(default_factory=lambda: [
        "update task", "change task", "modify task", "edit task", "rename task"
    ])
    priority: int = 10
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        query = input_data.query.lower()

        match = re.search(r"(?:update|change|modify|edit|rename)\s+task\s+(.+?)\s+to\s+(.+)", query)
        if not match:
            return SkillOutput(
                success=False,
                message="Please specify the task to update. Format: 'update task <current> to <new>'",
                suggestions=["update task old name to new name"]
            )

        current_desc = match.group(1).strip()
        new_desc = match.group(2).strip()

        async with httpx.AsyncClient() as client:
            try:
                tasks_response = await client.get(f"{self.backend_url}/tasks", timeout=10.0)
                if tasks_response.status_code != 200:
                    return SkillOutput(success=False, message="Error retrieving tasks")

                tasks = tasks_response.json()
                task_to_update = None

                for task in tasks:
                    if current_desc.lower() in task['title'].lower():
                        task_to_update = task
                        break

                if task_to_update:
                    update_response = await client.put(
                        f"{self.backend_url}/tasks/{task_to_update['id']}",
                        json={"title": new_desc},
                        timeout=10.0
                    )
                    if update_response.status_code == 200:
                        return SkillOutput(
                            success=True,
                            message=f"Updated task: '{current_desc}' -> '{new_desc}'",
                            data=update_response.json()
                        )
                    else:
                        return SkillOutput(
                            success=False,
                            message=f"Error updating task: {update_response.text}"
                        )
                else:
                    return SkillOutput(
                        success=False,
                        message=f"Task containing '{current_desc}' not found",
                        suggestions=["list tasks"]
                    )
            except Exception as e:
                return SkillOutput(
                    success=False,
                    message=f"Error: {str(e)}"
                )


@dataclass
class TaskToggleSkill(Skill):
    """Skill for toggling task completion"""
    name: str = "task_toggle"
    description: str = "Toggles task completion status"
    keywords: List[str] = field(default_factory=lambda: [
        "complete task", "finish task", "mark done", "toggle task",
        "uncomplete task", "mark pending", "done"
    ])
    priority: int = 10
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        query = input_data.query.lower()

        match = re.search(
            r"(?:complete|finish|toggle|mark\s+done|mark\s+pending|done)\s+(?:task\s+)?(.+)",
            query
        )
        if not match:
            return SkillOutput(
                success=False,
                message="Please specify which task to toggle. Format: 'complete task <description>'",
                suggestions=["complete task grocery shopping"]
            )

        task_desc = match.group(1).strip()

        async with httpx.AsyncClient() as client:
            try:
                tasks_response = await client.get(f"{self.backend_url}/tasks", timeout=10.0)
                if tasks_response.status_code != 200:
                    return SkillOutput(success=False, message="Error retrieving tasks")

                tasks = tasks_response.json()
                task_to_toggle = None

                for task in tasks:
                    if task_desc.lower() in task['title'].lower():
                        task_to_toggle = task
                        break

                if task_to_toggle:
                    toggle_response = await client.patch(
                        f"{self.backend_url}/tasks/{task_to_toggle['id']}/toggle",
                        timeout=10.0
                    )
                    if toggle_response.status_code == 200:
                        updated = toggle_response.json()
                        status = "completed" if updated['completed'] else "pending"
                        return SkillOutput(
                            success=True,
                            message=f"Task '{task_to_toggle['title']}' marked as {status}",
                            data=updated
                        )
                    else:
                        return SkillOutput(
                            success=False,
                            message=f"Error toggling task: {toggle_response.text}"
                        )
                else:
                    return SkillOutput(
                        success=False,
                        message=f"Task containing '{task_desc}' not found",
                        suggestions=["list tasks"]
                    )
            except Exception as e:
                return SkillOutput(
                    success=False,
                    message=f"Error: {str(e)}"
                )


@dataclass
class HelpSkill(Skill):
    """Skill for providing help and available commands"""
    name: str = "help"
    description: str = "Provides help and lists available commands"
    keywords: List[str] = field(default_factory=lambda: [
        "help", "commands", "what can you do", "how to", "usage"
    ])
    priority: int = 5

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        help_message = """**Task Management Assistant**

**Available Commands:**
- **Add Task:** "add task <description>"
- **List Tasks:** "list tasks" or "show tasks"
- **Delete Task:** "delete task <description>"
- **Update Task:** "update task <old> to <new>"
- **Complete Task:** "complete task <description>"

**Examples:**
- "add task buy groceries"
- "list tasks"
- "delete task groceries"
- "update task groceries to buy organic groceries"
- "complete task groceries"
"""
        return SkillOutput(
            success=True,
            message=help_message,
            suggestions=["list tasks", "add task example"]
        )


@dataclass
class GreetingSkill(Skill):
    """Skill for handling greetings"""
    name: str = "greeting"
    description: str = "Responds to user greetings"
    keywords: List[str] = field(default_factory=lambda: [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening"
    ])
    priority: int = 1

    async def execute(self, input_data: SkillInput) -> SkillOutput:
        return SkillOutput(
            success=True,
            message="Hello! I'm your task management assistant. How can I help you today?",
            suggestions=["list tasks", "add task", "help"]
        )


# Initialize skill registry with all skills
def create_skill_registry() -> SkillRegistry:
    """Create and populate the skill registry"""
    registry = SkillRegistry()

    registry.register(TaskCreationSkill())
    registry.register(TaskListingSkill())
    registry.register(TaskDeletionSkill())
    registry.register(TaskUpdateSkill())
    registry.register(TaskToggleSkill())
    registry.register(HelpSkill())
    registry.register(GreetingSkill())

    return registry


# Global skill registry
skill_registry = create_skill_registry()
