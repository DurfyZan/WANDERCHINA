
import uuid
from datetime import datetime
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from src.core.schemas import AgentPersona, InteractionNode, SocialDataPayload
from src.core.llm_router import LLMRouter
from src.agents.persona_manager import PersonaManager, HumanizationEngine


class AgentState(TypedDict):
    scenario: str
    location: str
    post_id: str
    main_content: Optional[str]
    author_persona: Optional[AgentPersona]
    interactions: List[InteractionNode]
    current_round: int
    max_rounds: int
    current_speaker: Optional[str]
    retry_feedback: Optional[str]


class CommunityInteractionGraph:
    def __init__(self, llm_provider: str = "deepseek"):
        self.llm = LLMRouter(provider=llm_provider)
        self.persona_manager = PersonaManager()
        self.humanizer = HumanizationEngine()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("init_scenario", self._init_scenario)
        graph.add_node("generate_post", self._generate_post)
        graph.add_node("local_agent_reply", self._local_agent_reply)
        graph.add_node("expat_agent_reply", self._expat_agent_reply)
        graph.add_node("check_rounds", self._check_rounds)
        graph.add_node("assemble_payload", self._assemble_payload)

        graph.set_entry_point("init_scenario")
        graph.add_edge("init_scenario", "generate_post")
        graph.add_edge("generate_post", "local_agent_reply")
        graph.add_edge("local_agent_reply", "expat_agent_reply")
        graph.add_edge("expat_agent_reply", "check_rounds")
        graph.add_conditional_edges(
            "check_rounds",
            lambda state: "continue" if state["current_round"] < state["max_rounds"] else "done",
            {
                "continue": "local_agent_reply",
                "done": "assemble_payload"
            }
        )
        graph.add_edge("assemble_payload", END)

        return graph.compile()

    def _init_scenario(self, state: AgentState) -> AgentState:
        tourist_persona = self.persona_manager.create_tourist_persona("agent_tourist_001")
        state["author_persona"] = tourist_persona
        state["current_round"] = 0
        state["max_rounds"] = 3
        state["interactions"] = []
        return state

    async def _generate_post(self, state: AgentState) -> AgentState:
        persona = state["author_persona"]
        system_prompt = self.persona_manager.build_system_prompt(persona)
        user_prompt = f"""你正在社交媒体上发一篇关于你经历的帖子。

场景：{state['scenario']}
地点：{state['location']}

请写一篇真实的社交媒体帖子，内容要具体、有个人感受，不要太正式。
150-300字左右。
只写帖子内容，不要加其他说明。"""

        response = await self.llm.agenerate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.9
        )
        humanized_content = self.humanizer.humanize(response.final_reply, persona)

        post_node = InteractionNode(
            node_id=str(uuid.uuid4()),
            parent_id=None,
            agent_id=persona.agent_id,
            content=humanized_content,
            raw_thinking=response.thinking_process,
            timestamp=datetime.now().isoformat()
        )

        state["main_content"] = humanized_content
        state["interactions"].append(post_node)
        state["current_speaker"] = "local"
        return state

    async def _local_agent_reply(self, state: AgentState) -> AgentState:
        local_persona = self.persona_manager.create_local_persona("agent_local_001")
        system_prompt = self.persona_manager.build_system_prompt(local_persona)

        context = self._build_context(state)
        user_prompt = f"""你在社交媒体上看到了一篇帖子，想回复一下。

【帖子和回复历史】
{context}

请根据你自己的人设写一条真实的回复。
50-150字左右。
只写回复内容，不要加其他说明。"""

        response = await self.llm.agenerate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.9
        )
        humanized_content = self.humanizer.humanize(response.final_reply, local_persona)

        parent_id = state["interactions"][-1].node_id if state["interactions"] else None
        reply_node = InteractionNode(
            node_id=str(uuid.uuid4()),
            parent_id=parent_id,
            agent_id=local_persona.agent_id,
            content=humanized_content,
            raw_thinking=response.thinking_process,
            timestamp=datetime.now().isoformat()
        )

        state["interactions"].append(reply_node)
        state["current_speaker"] = "expat"
        return state

    async def _expat_agent_reply(self, state: AgentState) -> AgentState:
        expat_persona = self.persona_manager.create_expat_persona("agent_expat_001")
        system_prompt = self.persona_manager.build_system_prompt(expat_persona)

        context = self._build_context(state)
        user_prompt = f"""你在社交媒体上看到了这篇帖子和回复，想加入讨论。

【帖子和回复历史】
{context}

请根据你自己的人设写一条真实的回复。
50-150字左右。
只写回复内容，不要加其他说明。"""

        response = await self.llm.agenerate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.9
        )
        humanized_content = self.humanizer.humanize(response.final_reply, expat_persona)

        parent_id = state["interactions"][-1].node_id if state["interactions"] else None
        reply_node = InteractionNode(
            node_id=str(uuid.uuid4()),
            parent_id=parent_id,
            agent_id=expat_persona.agent_id,
            content=humanized_content,
            raw_thinking=response.thinking_process,
            timestamp=datetime.now().isoformat()
        )

        state["interactions"].append(reply_node)
        state["current_round"] += 1
        state["current_speaker"] = "local"
        return state

    def _check_rounds(self, state: AgentState) -> AgentState:
        return state

    def _assemble_payload(self, state: AgentState) -> AgentState:
        return state

    def _build_context(self, state: AgentState) -> str:
        lines = []
        lines.append(f"【主帖】\n{state['main_content']}\n")
        for i, interaction in enumerate(state["interactions"][1:], 1):
            lines.append(f"【回复 {i}】\n{interaction.content}\n")
        return "\n".join(lines)

    async def arun(self, scenario: str, location: str) -> SocialDataPayload:
        initial_state: AgentState = {
            "scenario": scenario,
            "location": location,
            "post_id": str(uuid.uuid4()),
            "main_content": None,
            "author_persona": None,
            "interactions": [],
            "current_round": 0,
            "max_rounds": 3,
            "current_speaker": None,
            "retry_feedback": None
        }

        state = initial_state
        state = self._init_scenario(state)
        state = await self._generate_post(state)

        for _ in range(initial_state["max_rounds"]):
            state = await self._local_agent_reply(state)
            state = await self._expat_agent_reply(state)

        payload = SocialDataPayload(
            post_id=state["post_id"],
            main_content=state["main_content"] or "",
            location=state["location"],
            author_persona=state["author_persona"],
            interactions=state["interactions"],
            annotations={}
        )

        return payload
