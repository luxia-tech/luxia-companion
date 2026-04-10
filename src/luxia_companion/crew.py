from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from luxia_companion.tools.knowledge_search import search_knowledge_base


@CrewBase
class CompanionCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def knowledge_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config["knowledge_assistant"],
            tools=[search_knowledge_base],
        )

    @task
    def answer_partner_query(self) -> Task:
        return Task(config=self.tasks_config["answer_partner_query"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def answer(query: str) -> str:
    companion = CompanionCrew()
    result = companion.crew().kickoff(inputs={"user_query": query})
    return str(result).strip()
