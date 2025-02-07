from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class AnalyzerCrew():
	"""AnalyzerCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def fii_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['fii_analyst'],
			verbose=True
		)

	@agent
	def report_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['report_writer'],
			verbose=True
		)

	@task
	def fii_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['fii_analyst_task'],
		)
	@task
	def report_writer_task(self) -> Task:
		return Task(
			config=self.tasks_config['report_writer_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AnalyzerCrew crew"""

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
