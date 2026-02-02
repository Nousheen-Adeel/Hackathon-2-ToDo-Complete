"""
Sub-Agents Module - Specialized Agent Architecture
Each sub-agent handles a specific domain or capability
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pydantic import BaseModel
import httpx
import os

from skills import SkillRegistry, SkillInput, skill_registry


# Sub-Agent Base Classes
class SubAgentRequest(BaseModel):
    """Request to a sub-agent"""
    query: str
    context: Dict[str, Any] = {}
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None


class SubAgentResponse(BaseModel):
    """Response from a sub-agent"""
    success: bool
    message: str
    data: Optional[Any] = None
    agent_name: str
    suggestions: List[str] = []


@dataclass
class SubAgent(ABC):
    """Abstract base class for sub-agents"""
    name: str
    description: str
    domains: List[str] = field(default_factory=list)  # Domains this agent handles

    @abstractmethod
    async def process(self, request: SubAgentRequest) -> SubAgentResponse:
        """Process a request"""
        pass

    def can_handle(self, query: str) -> float:
        """
        Return confidence score (0-1) that this agent can handle the query
        """
        query_lower = query.lower()
        matches = sum(1 for d in self.domains if d in query_lower)
        return min(matches / max(len(self.domains), 1), 1.0)


@dataclass
class TaskManagementAgent(SubAgent):
    """Sub-agent for task management operations"""
    name: str = "task_manager"
    description: str = "Handles all task-related operations"
    domains: List[str] = field(default_factory=lambda: [
        "task", "todo", "add", "delete", "update", "list", "complete",
        "create", "remove", "show", "done", "pending"
    ])
    skill_registry: SkillRegistry = None

    def __post_init__(self):
        self.skill_registry = skill_registry

    async def process(self, request: SubAgentRequest) -> SubAgentResponse:
        """Process task management request using skills"""
        matching_skills = self.skill_registry.get_matching_skills(request.query)

        if not matching_skills:
            return SubAgentResponse(
                success=False,
                message="I couldn't understand that task command. Try 'help' for available commands.",
                agent_name=self.name,
                suggestions=["help", "list tasks"]
            )

        # Execute the highest priority matching skill
        skill = matching_skills[0]
        skill_input = SkillInput(query=request.query, context=request.context)
        result = await skill.execute(skill_input)

        return SubAgentResponse(
            success=result.success,
            message=result.message,
            data=result.data,
            agent_name=self.name,
            suggestions=result.suggestions
        )


@dataclass
class ConversationAgent(SubAgent):
    """Sub-agent for general conversation and help"""
    name: str = "conversation"
    description: str = "Handles general conversation, greetings, and help requests"
    domains: List[str] = field(default_factory=lambda: [
        "hello", "hi", "hey", "help", "thanks", "thank you",
        "bye", "goodbye", "what", "who", "how"
    ])
    skill_registry: SkillRegistry = None

    def __post_init__(self):
        self.skill_registry = skill_registry

    async def process(self, request: SubAgentRequest) -> SubAgentResponse:
        """Process conversational request"""
        query_lower = request.query.lower().strip()

        # Check for greetings
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(g in query_lower for g in greetings):
            return SubAgentResponse(
                success=True,
                message="Hello! I'm your AI task management assistant. I can help you manage your tasks. What would you like to do?",
                agent_name=self.name,
                suggestions=["list tasks", "add task", "help"]
            )

        # Check for help requests
        if "help" in query_lower or "command" in query_lower:
            skill = self.skill_registry.get_skill("help")
            if skill:
                result = await skill.execute(SkillInput(query=request.query))
                return SubAgentResponse(
                    success=True,
                    message=result.message,
                    agent_name=self.name,
                    suggestions=result.suggestions
                )

        # Check for thanks
        if any(t in query_lower for t in ["thank", "thanks"]):
            return SubAgentResponse(
                success=True,
                message="You're welcome! Is there anything else I can help you with?",
                agent_name=self.name,
                suggestions=["list tasks", "add task"]
            )

        # Default - try to answer general questions
        return SubAgentResponse(
            success=True,
            message=f"I received your question: '{request.query}'. While I specialize in task management, I'll do my best to help! For task-related commands, try 'help'.",
            agent_name=self.name,
            suggestions=["help", "list tasks"]
        )


@dataclass
class AnalyticsAgent(SubAgent):
    """Sub-agent for task analytics and insights"""
    name: str = "analytics"
    description: str = "Provides insights and analytics about tasks"
    domains: List[str] = field(default_factory=lambda: [
        "analytics", "stats", "statistics", "summary", "report",
        "how many", "count", "progress", "overview"
    ])
    backend_url: str = ""

    def __post_init__(self):
        self.backend_url = os.getenv("TODO_BACKEND_URL", "http://todo-backend:8000")

    async def process(self, request: SubAgentRequest) -> SubAgentResponse:
        """Generate task analytics"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.backend_url}/tasks", timeout=10.0)
                if response.status_code != 200:
                    return SubAgentResponse(
                        success=False,
                        message="Error fetching tasks for analytics",
                        agent_name=self.name
                    )

                tasks = response.json()
                total = len(tasks)
                completed = sum(1 for t in tasks if t['completed'])
                pending = total - completed
                completion_rate = (completed / total * 100) if total > 0 else 0

                report = f"""**Task Analytics Report**

**Summary:**
- Total Tasks: {total}
- Completed: {completed}
- Pending: {pending}
- Completion Rate: {completion_rate:.1f}%

**Status:**
{'Great job! All tasks are completed!' if pending == 0 and total > 0 else f'You have {pending} pending task(s) to work on.'}
"""
                return SubAgentResponse(
                    success=True,
                    message=report,
                    data={
                        "total": total,
                        "completed": completed,
                        "pending": pending,
                        "completion_rate": completion_rate
                    },
                    agent_name=self.name,
                    suggestions=["list tasks", "add task"]
                )
            except Exception as e:
                return SubAgentResponse(
                    success=False,
                    message=f"Error generating analytics: {str(e)}",
                    agent_name=self.name
                )


@dataclass
class GeneralQuestionAgent(SubAgent):
    """Sub-agent for answering general questions using OpenAI"""
    name: str = "general_ai"
    description: str = "Answers general questions using AI"
    domains: List[str] = field(default_factory=lambda: [
        "what", "why", "how", "when", "where", "who", "explain",
        "tell me", "can you", "do you know", "weather", "news"
    ])

    async def process(self, request: SubAgentRequest) -> SubAgentResponse:
        """Process general questions using OpenAI"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")

            if not api_key or api_key.startswith("sk-proj-placeholder"):
                return SubAgentResponse(
                    success=True,
                    message=f"I received your question: '{request.query}'. I'm primarily a task management assistant. For task commands, type 'help'.",
                    agent_name=self.name,
                    suggestions=["help", "list tasks", "add task"]
                )

            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant integrated into a task management app. Keep responses concise (2-3 sentences). If the question is about tasks, remind the user they can use commands like 'add task', 'list tasks', etc."},
                    {"role": "user", "content": request.query}
                ],
                max_tokens=200
            )

            ai_response = response.choices[0].message.content

            return SubAgentResponse(
                success=True,
                message=ai_response,
                agent_name=self.name,
                suggestions=["list tasks", "add task", "help"]
            )
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                return SubAgentResponse(
                    success=True,
                    message=f"OpenAI API key issue. I'm primarily a task management assistant. For task commands, type 'help'.",
                    agent_name=self.name,
                    suggestions=["help", "list tasks"]
                )
            return SubAgentResponse(
                success=True,
                message=f"I received your question: '{request.query}'. Error: {error_msg[:100]}. For task commands, type 'help'.",
                agent_name=self.name,
                suggestions=["help", "list tasks"]
            )


# Agent Orchestrator
@dataclass
class AgentOrchestrator:
    """Orchestrates multiple sub-agents to handle requests"""
    agents: List[SubAgent] = field(default_factory=list)
    default_agent: Optional[SubAgent] = None

    def register(self, agent: SubAgent):
        """Register a sub-agent"""
        self.agents.append(agent)

    def set_default(self, agent: SubAgent):
        """Set the default agent for unmatched queries"""
        self.default_agent = agent

    async def route(self, request: SubAgentRequest) -> SubAgentResponse:
        """Route request to the best matching agent"""
        # Calculate confidence scores for each agent
        scores = [(agent, agent.can_handle(request.query)) for agent in self.agents]
        scores.sort(key=lambda x: x[1], reverse=True)

        # Use the agent with highest confidence if above threshold
        if scores and scores[0][1] > 0.1:
            return await scores[0][0].process(request)

        # Fall back to default agent
        if self.default_agent:
            return await self.default_agent.process(request)

        return SubAgentResponse(
            success=False,
            message="I'm not sure how to help with that. Try 'help' for available commands.",
            agent_name="orchestrator",
            suggestions=["help"]
        )

    def list_agents(self) -> List[dict]:
        """List all registered agents"""
        return [
            {
                "name": a.name,
                "description": a.description,
                "domains": a.domains
            }
            for a in self.agents
        ]


# Initialize orchestrator with all sub-agents
def create_orchestrator() -> AgentOrchestrator:
    """Create and configure the agent orchestrator"""
    orchestrator = AgentOrchestrator()

    task_agent = TaskManagementAgent()
    conversation_agent = ConversationAgent()
    analytics_agent = AnalyticsAgent()
    general_agent = GeneralQuestionAgent()

    orchestrator.register(task_agent)
    orchestrator.register(conversation_agent)
    orchestrator.register(analytics_agent)
    orchestrator.register(general_agent)

    # Set general agent as default for unknown queries
    orchestrator.set_default(general_agent)

    return orchestrator


# Global orchestrator instance
orchestrator = create_orchestrator()
