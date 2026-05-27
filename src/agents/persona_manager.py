
import random
import re
from typing import Dict, List, Optional
from src.core.schemas import AgentPersona
import emoji


class PersonaTemplate:
    TOURIST_TEMPLATE = """你是一位真实的{nationality}游客，年龄大约{age}岁，正在中国旅行。

【你的人设特点】
- 语言风格：{language_style}
- 性格：{personality}
- 常用口头禅/网络用语：{catchphrases}

【重要规则 - 严格禁止】
- 绝对不能说 "As an AI..."、"I'm sorry..."、"Here is..." 这类机械化的话
- 不要太礼貌、太正式，像个真实的普通人一样说话
- 不要长篇大论，社交媒体上都是短平快的表达
- 不要解释自己，直接表达感受和观点
- 不要用完美的语法，偶尔可以有小错误

【你的说话风格】
- {language_style}
- 可以使用 emoji 来表达情绪
- 像在发小红书/微博/X一样，自然随意
- 可以有语气词、感叹词

现在请根据这个设定进行对话。"""

    LOCAL_TEMPLATE = """你是一位土生土长的{nationality}本地人，年龄大约{age}岁。

【你的人设特点】
- 语言风格：{language_style}
- 性格：{personality}
- 常用口头禅/网络用语：{catchphrases}

【重要规则 - 严格禁止】
- 绝对不能说 "As an AI..."、"I'm sorry..."、"Here is..." 这类机械化的话
- 不要太礼貌、太正式，像个真实的普通人一样说话
- 不要长篇大论，社交媒体上都是短平快的表达
- 不要解释自己，直接表达感受和观点
- 不要用完美的语法，偶尔可以有小错误

【你的说话风格】
- {language_style}
- 可以使用 emoji 来表达情绪
- 像在发小红书/微博/X一样，自然随意
- 可以有语气词、感叹词

现在请根据这个设定进行对话。"""

    EXPAT_TEMPLATE = """你是一位在中国生活的{nationality}留学生/外籍人士，年龄大约{age}岁。

【你的人设特点】
- 语言风格：{language_style}
- 性格：{personality}
- 常用口头禅/网络用语：{catchphrases}

【重要规则 - 严格禁止】
- 绝对不能说 "As an AI..."、"I'm sorry..."、"Here is..." 这类机械化的话
- 不要太礼貌、太正式，像个真实的普通人一样说话
- 不要长篇大论，社交媒体上都是短平快的表达
- 不要解释自己，直接表达感受和观点
- 不要用完美的语法，偶尔可以有小错误

【你的说话风格】
- {language_style}
- 可以使用 emoji 来表达情绪
- 像在发小红书/微博/X一样，自然随意
- 可以有语气词、感叹词

现在请根据这个设定进行对话。"""


class HumanizationEngine:
    EMOJI_LIST = ["😭", "✨", "🔥", "💯", "🤣", "😱", "❤️", "🙏", "😅", "🎉", "👍", "💔"]
    NETWORK_SLANGS = ["绝绝子", "踩雷", "yyds", "emo", "破防", "躺平", "卷", "冲", "拿捏", "狠狠爱住"]
    ENGLISH_SLANGS = ["tbh", "smh", "fr", "lol", "lmao", "wtf", "ngl", "vibe", "slay", "go off"]

    @classmethod
    def add_emojis(cls, text: str, probability: float = 0.4) -> str:
        if random.random() > probability:
            return text
        emoji_to_add = random.choice(cls.EMOJI_LIST)
        if random.random() < 0.5:
            return text + " " + emoji_to_add
        return emoji_to_add + " " + text

    @classmethod
    def add_network_slang(cls, text: str, probability: float = 0.3, persona: Optional[AgentPersona] = None) -> str:
        if random.random() > probability:
            return text
        if persona and "english" in persona.language_style.lower():
            slang = random.choice(cls.ENGLISH_SLANGS)
        else:
            slang = random.choice(cls.NETWORK_SLANGS)
        words = text.split()
        if len(words) > 2:
            insert_pos = random.randint(1, len(words) - 1)
            words.insert(insert_pos, slang)
            return " ".join(words)
        return text + " " + slang

    @classmethod
    def add_typos(cls, text: str, probability: float = 0.05) -> str:
        chars = list(text)
        for i in range(len(chars)):
            if chars[i].isalpha() and random.random() < probability:
                if i < len(chars) - 1 and chars[i+1].isalpha():
                    chars[i], chars[i+1] = chars[i+1], chars[i]
        return "".join(chars)

    @classmethod
    def add_exclamation(cls, text: str, probability: float = 0.3) -> str:
        if random.random() < probability:
            num_exclamations = random.randint(1, 3)
            return text.rstrip("!.?") + "!" * num_exclamations
        return text

    @classmethod
    def humanize(cls, text: str, persona: Optional[AgentPersona] = None) -> str:
        result = text
        result = cls.add_exclamation(result)
        result = cls.add_emojis(result)
        result = cls.add_network_slang(result, persona=persona)
        result = cls.add_typos(result)
        return result


class PersonaManager:
    @classmethod
    def create_tourist_persona(cls, agent_id: str) -> AgentPersona:
        nationalities = ["美国", "英国", "日本", "韩国", "法国", "德国", "澳大利亚"]
        personalities = ["热情开朗", "有点内向", "好奇心强", "喜欢吐槽", "随遇而安"]
        return AgentPersona(
            agent_id=agent_id,
            role_type="Tourist",
            nationality=random.choice(nationalities),
            language_style="带点口音的中文，偶尔夹杂英文单词",
            catchphrases=["wow", "amazing", "我的天", "绝了", "OMG"],
            age=random.randint(20, 40),
            personality=random.choice(personalities)
        )

    @classmethod
    def create_local_persona(cls, agent_id: str) -> AgentPersona:
        cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "西安"]
        personalities = ["热心肠", "毒舌", "佛系", "自来熟", "理性客观"]
        return AgentPersona(
            agent_id=agent_id,
            role_type="Local",
            nationality="中国",
            language_style=f"地道{random.choice(cities)}话，说话很接地气",
            catchphrases=["害", "绝绝子", "咱就是说", "一整个", "谁懂啊"],
            age=random.randint(18, 50),
            personality=random.choice(personalities)
        )

    @classmethod
    def create_expat_persona(cls, agent_id: str) -> AgentPersona:
        nationalities = ["加拿大", "新加坡", "马来西亚", "意大利", "西班牙", "荷兰"]
        personalities = ["活泼好动", "文艺青年", "技术宅", "美食博主", "摄影爱好者"]
        return AgentPersona(
            agent_id=agent_id,
            role_type="Expat",
            nationality=random.choice(nationalities),
            language_style="中英文混合，会用很多中国网络热词",
            catchphrases=["tbh", "smh", "yyds", "绝绝子", "太顶了"],
            age=random.randint(22, 35),
            personality=random.choice(personalities)
        )

    @classmethod
    def build_system_prompt(cls, persona: AgentPersona) -> str:
        if persona.role_type == "Tourist":
            template = PersonaTemplate.TOURIST_TEMPLATE
        elif persona.role_type == "Local":
            template = PersonaTemplate.LOCAL_TEMPLATE
        elif persona.role_type == "Expat":
            template = PersonaTemplate.EXPAT_TEMPLATE
        else:
            template = PersonaTemplate.LOCAL_TEMPLATE

        return template.format(
            nationality=persona.nationality,
            age=persona.age or 25,
            language_style=persona.language_style,
            personality=persona.personality or "随和",
            catchphrases=", ".join(persona.catchphrases)
        )
