#!/usr/bin/env python
# Add these lines at the top
import sys
import os


# Then continue with your existing imports
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from crews.retriever_crew.retriever_crew import RetrieverCrew
from crews.analyzer_crew.analyzer_crew import AnalyzerCrew
from dotenv import load_dotenv
import streamlit as st
import os
from datetime import datetime


load_dotenv()


class LightHouseFiis(BaseModel):
    fiis: list = []
    date: str = ""
    fiis_scrapped: list = []


class LightHouseFiisFlow(Flow[LightHouseFiis]):

    @start()
    def get_fiis_to_analyze(self):
        self.state.date = datetime.now().strftime("%Y/%m/%d")

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
            "fiis_scrapped": self.state.fiis_scrapped,
            "date": self.state.date
        }

        analyzer_crew.crew().kickoff(inputs)


def kickoff():
    lighthouse_fiis = LightHouseFiisFlow()
    lighthouse_fiis.kickoff()


if __name__ == "__main__":
    st.set_page_config(page_title="FIIs Report Generator")
    st.title("Gerador de Relatório de FIIs")

    # Form screen
    st.header("Inserir Nomes dos FIIs")
    fii_names = st.text_area("Digite os nomes dos FIIs separados por vírgula:")

    if st.button("Gerar relatório"):
        if fii_names.strip():
            # Processing the FIIs
            fii_list = [fii.strip() for fii in fii_names.split(",")]
            
            # Placeholder for report generation logic
            with st.spinner("Gerando relatório..."):
                lighthouse_flow = LightHouseFiisFlow()
                lighthouse_flow.state.fiis = fii_list  # Setting the state with the list of FIIs
                lighthouse_flow.kickoff()
                
                report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../report.md"))
            
                try:
                    with open(report_path, "r", encoding="utf-8") as file:
                        report = file.read()
                        
                        from openai import OpenAI
                        client = OpenAI()

                        completion = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "you are a analyzer of information about investiments and checker of not well filled information"
                                },
                                 {
                                    "role": "user",
                                    "content": f"""
                                        look at this information about a Fundo de Investimento Imobiliario: {report}, and return True if it is filled well, or False if some values is not informed.
                                        expected output: True or False
                                    """
                                }
                            ]
                        )

                        is_info_ok = completion.choices[0].message.content
                        print(f"is info ok: {is_info_ok}")
                        print()
                        if is_info_ok == "False":
                            st.warning("Não foi possivel encontrar dados completos. Por favor, tente de novo.")                        
                        
                except FileNotFoundError:
                    report = "O arquivo report.md não foi encontrado. Verifique se o processo de geração do relatório foi concluído com sucesso."


            # Display the report
            st.header("Relatório Gerado")
            if is_info_ok == "False":
                st.markdown(None)
            else:
                st.markdown(report)
        else:
            st.warning("Por favor, insira pelo menos um nome de FII.")