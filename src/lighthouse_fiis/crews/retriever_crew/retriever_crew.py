from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool


@CrewBase
class RetrieverCrew:
    
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def fii_info_scrapper(self) -> Agent:
        return Agent(
            config=self.agents_config["fii_info_scrapper"],
            tools=[ScrapeWebsiteTool()]
        )

    @task
    def fii_info_scrapper_task(self) -> Task:
        return Task(
            config=self.tasks_config["fii_info_scrapper_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )
