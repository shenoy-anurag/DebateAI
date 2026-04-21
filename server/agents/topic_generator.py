import json
from typing import List
from dataclasses import dataclass

from agents.base import BaseAgent, AgentResponse
from rag.retriever import CitationRetriever


@dataclass
class DebateTopic:
    topic: str
    pro_premise: str
    con_premise: str


TOPIC_GENERATOR_PROMPT = """You are an expert research topic generator. Your task is to analyze a research paper and generate interesting debate topics.

Generate exactly 3 debate topics that would be compelling for academic debate. Each topic should have:
1. A clear, specific question or statement that can be debated
2. A Pro premise (reason to agree)
3. A Con premise (reason to disagree)

Format your response as a JSON array with the following structure:
[
  {
    "topic": "The debate question/topic",
    "pro_premise": "Key argument for the Pro position",
    "con_premise": "Key argument for the Con position"
  }
]

Focus on topics that:
- Are substantive and meaningful for the research field
- Have clear arguments on both sides
- Are relevant to the paper's contributions
- Would generate insightful discussion

Return ONLY valid JSON, no other text."""


class TopicGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=TOPIC_GENERATOR_PROMPT,
            model_name="gpt-4o-mini",
            temperature=0.8
        )

    def process(self, paper_content: str, **kwargs) -> AgentResponse:
        prompt = f"""Analyze the following research paper and generate 3 debate topics:

{paper_content[:8000]}

Generate exactly 3 debate topics in the specified JSON format."""

        content = self._call_llm(prompt)
        
        try:
            topics_data = json.loads(content)
            topics = [
                DebateTopic(
                    topic=t["topic"],
                    pro_premise=t["pro_premise"],
                    con_premise=t["con_premise"]
                )
                for t in topics_data
            ]
        except json.JSONDecodeError:
            topics = []
        
        return AgentResponse(
            content=content,
            citations=[],
            metadata={"topics": [{"topic": t.topic, "pro_premise": t.pro_premise, "con_premise": t.con_premise} for t in topics]}
        )


class TopicGeneratorWithRAG:
    def __init__(self, session_id: str):
        self.retriever = CitationRetriever(session_id)
        self.agent = TopicGeneratorAgent()

    def generate_topics(self, query: str = None) -> List[DebateTopic]:
        if query is None:
            query = "main contributions, methodology, findings, implications"
        
        context = self.retriever.get_context_string(query, top_k=10)
        
        response = self.agent.process(context)
        
        if response.metadata and "topics" in response.metadata:
            return [
                DebateTopic(
                    topic=t["topic"],
                    pro_premise=t["pro_premise"],
                    con_premise=t["con_premise"]
                )
                for t in response.metadata["topics"]
            ]
        
        return []
