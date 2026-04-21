from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

import config
from agents.base import AgentResponse
from agents.debate_agent import DebateAgent, DebateRole, DebateTurn
from agents.topic_generator import DebateTopic


class DebateStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class DebateState:
    session_id: str
    topic: str
    pro_premise: str
    con_premise: str
    status: DebateStatus = DebateStatus.PENDING
    turns: List[DebateTurn] = field(default_factory=list)
    current_turn: int = 0
    winner: Optional[str] = None
    summary: Optional[str] = None


MANAGER_SYSTEM_PROMPT = """You are a debate manager. Your role is to:
1. Evaluate debate turns for quality and citation
2. Determine when the debate should end (max rounds or convergence)
3. Generate a final summary declaring a winner

You must evaluate:
- Citation rate (are claims backed by sources?)
- Rebuttal quality (addressing opponent's specific points)
- Convergence (are arguments repeating?)

Respond with one of:
- "CONTINUE": Debate should continue
- "END_CONVERGENCE": Both sides have converged (agree or repeat)
- "END_MAX_TURNS": Maximum turns reached

When ending, provide a summary declaring which side presented stronger arguments."""


class DebateManager:
    def __init__(
        self,
        session_id: str,
        topic: str,
        pro_premise: str,
        con_premise: str
    ):
        self.session_id = session_id
        self.topic = topic
        self.pro_premise = pro_premise
        self.con_premise = con_premise
        
        self.state = DebateState(
            session_id=session_id,
            topic=topic,
            pro_premise=pro_premise,
            con_premise=con_premise
        )
        
        self.pro_agent = DebateAgent(
            role=DebateRole.PRO,
            session_id=session_id,
            topic=topic,
            premise=pro_premise
        )
        
        self.con_agent = DebateAgent(
            role=DebateRole.CON,
            session_id=session_id,
            topic=topic,
            premise=con_premise
        )
        
        self.manager_llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=0.3,
            api_key=config.OPENAI_API_KEY
        )
        
        self.manager_messages = [
            SystemMessage(content=MANAGER_SYSTEM_PROMPT)
        ]

    def start(self) -> DebateTurn:
        self.state.status = DebateStatus.ACTIVE
        self.state.current_turn = 1
        
        pro_turn = self.pro_agent.process(turn_number=1)
        self.state.turns.append(pro_turn)
        
        return pro_turn

    def next_turn(self) -> Optional[DebateTurn]:
        self.state.current_turn += 1
        
        last_turn = self.state.turns[-1]
        opponent_turn = self.state.turns[-2] if len(self.state.turns) >= 2 else None
        
        if last_turn.role == DebateRole.PRO:
            next_turn = self.con_agent.process(
                turn_number=self.state.current_turn,
                opponent_turn=opponent_turn
            )
        else:
            next_turn = self.pro_agent.process(
                turn_number=self.state.current_turn,
                opponent_turn=opponent_turn
            )
        
        self.state.turns.append(next_turn)
        
        return next_turn

    def _evaluate_continuation(self) -> tuple[bool, str]:
        turns_text = "\n\n".join([
            f"Turn {t.turn_number} ({t.role.value}): {t.content[:200]}..."
            for t in self.state.turns[-4:]
        ])
        
        prompt = f"""Evaluate this debate:

Topic: {self.topic}

Recent turns:
{turns_text}

Current turn: {self.state.current_turn}
Max turns: {config.DEBATE_MAX_TURNS}

Should the debate continue? Respond with:
- "CONTINUE" if the debate should proceed
- "END_CONVERGENCE" if arguments are repeating or converging
- "END_MAX_TURNS" if maximum turns reached

Also provide a brief reason for your decision."""

        response = self.manager_llm.invoke(
            self.manager_messages + [HumanMessage(content=prompt)]
        )
        
        content = response.content.upper()
        
        if "END" in content:
            return False, response.content
        return True, response.content

    def should_continue(self) -> bool:
        if self.state.current_turn >= config.DEBATE_MAX_TURNS:
            return False
        
        should_continue, reason = self._evaluate_continuation()
        return should_continue

    def end_debate(self) -> AgentResponse:
        self.state.status = DebateStatus.COMPLETED
        
        summary_prompt = f"""Generate a final debate summary and declare a winner.

Topic: {self.topic}
Pro Premise: {self.pro_premise}
Con Premise: {self.con_premise}

Debate Turns:
{chr(10).join([f"Turn {t.turn_number} ({t.role.value}): {t.content}" for t in self.state.turns])}

Provide:
1. Summary of key arguments from both sides
2. Evaluation of citation quality
3. Which side presented stronger arguments and why
4. Final verdict"""

        response = self.manager_llm.invoke(
            self.manager_messages + [HumanMessage(content=summary_prompt)]
        )
        
        self.state.summary = response.content
        
        if "PRO" in response.content.upper()[:50]:
            self.state.winner = "pro"
        elif "CON" in response.content.upper()[:50]:
            self.state.winner = "con"
        else:
            self.state.winner = "tie"
        
        return AgentResponse(
            content=response.content,
            citations=[],
            metadata={"winner": self.state.winner}
        )

    def get_state(self) -> DebateState:
        return self.state
