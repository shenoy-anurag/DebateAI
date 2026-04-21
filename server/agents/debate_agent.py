import re
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

from agents.base import BaseAgent, AgentResponse
from rag.retriever import CitationRetriever, Citation


class DebateRole(Enum):
    PRO = "pro"
    CON = "con"


DEBATE_AGENT_SYSTEM_PROMPT = """You are a research debate agent. Your role is to argue {role} the given topic in a debate about a research paper.

CRITICAL REQUIREMENTS:
1. You MUST cite the research paper for EVERY claim you make
2. Use citations in format: [Page X] or [Source Name]
3. If you cannot find evidence in the provided context, state that clearly
4. Address counterarguments from the opposing side when relevant
5. Be scholarly, factual, and focused on evidence from the paper

Your response should:
- Present clear arguments supporting your position
- Reference specific sections/pages from the research paper
- Address the opponent's previous arguments (if any)
- Be 2-4 paragraphs in length

Remember: Your credibility depends on citing sources accurately."""


@dataclass
class DebateTurn:
    role: DebateRole
    content: str
    citations: List[Citation]
    turn_number: int


class DebateAgent(BaseAgent):
    def __init__(
        self,
        role: DebateRole,
        session_id: str,
        topic: str,
        premise: str,
        model_name: str = None
    ):
        self.role = role
        self.session_id = session_id
        self.topic = topic
        self.premise = premise
        self.retriever = CitationRetriever(session_id)
        
        system_prompt = DEBATE_AGENT_SYSTEM_PROMPT.format(
            role="FOR" if role == DebateRole.PRO else "AGAINST"
        )
        
        super().__init__(
            system_prompt=system_prompt,
            model_name=model_name,
            temperature=0.7
        )

    def _build_context(self, opponent_turn: Optional[DebateTurn] = None) -> str:
        context = f"""DEBATE TOPIC: {self.topic}
YOUR PREMISE: {self.premise}

Relevant context from the research paper:
{self.retriever.get_context_string(self.topic, top_k=8)}
"""
        if opponent_turn:
            context += f"""
OPPONENT'S PREVIOUS ARGUMENT:
{opponent_turn.content}
CITATIONS: {self.retriever.format_citations(opponent_turn.citations)}
"""
        return context

    def _extract_citations(self, content: str) -> List[Citation]:
        citation_pattern = r'\[(?:Page\s*(\d+)|([^\]]+))\]'
        matches = re.findall(citation_pattern, content)
        
        citations = []
        for page_num, source in matches:
            citations.append(Citation(
                text="",
                source=source.strip() if source else "",
                page=int(page_num) if page_num else None
            ))
        
        return citations

    def process(
        self, 
        turn_number: int,
        opponent_turn: Optional[DebateTurn] = None,
        **kwargs
    ) -> DebateTurn:
        context = self._build_context(opponent_turn)
        
        if turn_number == 1:
            prompt = f"""{context}

This is your opening statement. Present your main arguments FOR your position. Cite sources from the paper."""
        elif opponent_turn:
            prompt = f"""{context}

This is a rebuttal. Address the opponent's arguments above and present new supporting arguments. Cite sources."""
        else:
            prompt = f"""{context}

Continue the debate with your next argument. Cite sources."""
        
        content = self._call_llm(prompt)
        citations = self._extract_citations(content)
        
        return DebateTurn(
            role=self.role,
            content=content,
            citations=citations,
            turn_number=turn_number
        )
