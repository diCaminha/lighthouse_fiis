#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from crews.retriever_crew.retriever_crew import RetrieverCrew

from crews.analyzer_crew.analyzer_crew import AnalyzerCrew

from dotenv import load_dotenv

load_dotenv()

class LightHouseFiis(BaseModel):
    fiis: list = []
    date: str = ""
    fiis_scrapped: list = []


class LightHouseFiisFlow(Flow[LightHouseFiis]):

    @start()
    def get_fiis_to_analyze(self):
        self.state.fiis = ["RECT11", "VINO11"]
        self.state.date = "2025-02-05"

    @listen(get_fiis_to_analyze)
    def retrieve_info_fiis(self):
        print("Retrieving information from list of fiis")
        
        retriever_crew = RetrieverCrew()

        inputs = {
            "fiis": self.state.fiis,
            "date": self.state.date
        }


        output = retriever_crew.crew().kickoff(inputs)
        self.state.fiis_scrapped = "\n".join([task.raw for task in output.tasks_output])
        
    @listen(retrieve_info_fiis)
    def analyze_specialist_fiis(self):

        analyzer_crew = AnalyzerCrew()

        inputs = {
            "fiis_scrapped": self.state.fiis_scrapped
        }

        analyzer_crew.crew().kickoff(inputs)


def kickoff():
    lighthouse_fiis = LightHouseFiisFlow()
    lighthouse_fiis.kickoff()


if __name__ == "__main__":
    kickoff()
