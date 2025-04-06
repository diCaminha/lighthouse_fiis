#!/usr/bin/env python
import sys
import os
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from crews.retriever_crew.retriever_crew import RetrieverCrew
from crews.analyzer_crew.analyzer_crew import AnalyzerCrew
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
from pymongo import MongoClient


load_dotenv()


__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


client = MongoClient(os.environ["URL_DB_MONGO"])

db = client.lighthousefiis
collection = db.fiis
is_info_ok = True

available_fiis = [
    'ABCP11', 'ALZR11', 'BBPO11', 'BCFF11', 'BCIA11', 'BRCR11', 'CSHG11',
    'CTNM11', 'CPTS11', 'FEXC11', 'FIIB11', 'FIIH11', 'GGRC11', 'HABT11',
    'HABR11', 'HGFF11', 'HGBS11', 'HGLG11', 'HGRE11', 'HGRU11', 'HSML11',
    'HFOF11', 'IRDM11', 'JSRE11', 'KNCR11', 'KNIP11', 'KNRI11', 'KFOF11',
    'MXRF11', 'PORD11', 'RBRD11', 'RBRF11', 'RBRR11', 'RBRP11', 'RBRY11',
    'TRXF11', 'VRTA11', 'VRLG11', 'VINO11', 'VISC11', 'XPCC11', 'XPIN11', 'XPML11'
]

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

    st.header("Selecionar FIIs")
    selected_fii = st.selectbox("Selecione os FIIs:", options=available_fiis)

    if st.button("Gerar relatório"):
        if selected_fii:
            
            document = collection.find_one({"fii": selected_fii})

            if document:
                report = document["report"]
                is_info_ok = True
                
            else:
                with st.spinner("Gerando relatório..."):
                    lighthouse_flow = LightHouseFiisFlow()
                    lighthouse_flow.state.fiis = selected_fii
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
                            if is_info_ok == "False":
                                st.warning("Não foi possível encontrar dados completos. Por favor, tente de novo.")
                            
                            else:
                                # salvar key document: selected_fii -> report
                                print(f"saving {selected_fii} on db.")   
                                collection.insert_one({"fii": selected_fii, "report": report})                    
                            
                    except FileNotFoundError:
                        report = "O arquivo report.md não foi encontrado. Verifique se o processo de geração do relatório foi concluído com sucesso."

                
            st.header("Relatório Gerado")
            if is_info_ok == "False":
                st.markdown("")
            else:
                st.markdown(report)
        else:
            st.warning("Por favor, selecione pelo menos um FII.")
