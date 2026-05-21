
import json
from datetime import datetime
from src.core.schemas import AgentPersona, InteractionNode, SocialDataPayload
from src.data.dataset_exporter import DatasetExporter


def main():
    print("=" * 60)
    print("子网页智能体数据生成与标注系统 - 演示模式")
    print("=" * 60)

    sample_persona = AgentPersona(
        agent_id="agent_tourist_demo",
        role_type="Tourist",
        nationality="美国",
        language_style="带点口音的中文，偶尔夹杂英文单词",
        catchphrases=["wow", "amazing", "我的天", "绝了", "OMG"],
        age=28,
        personality="热情开朗"
    )

    sample_interactions = [
        InteractionNode(
            node_id="post_001",
            parent_id=None,
            agent_id="agent_tourist_demo",
            content="刚到北京就被地铁搞懵了！想说用手机支付结果发现要实名认证... 害，我一个老外真的搞不定啊！有没有大神教教我！救命！",
            timestamp=datetime.now().isoformat()
        ),
        InteractionNode(
            node_id="reply_001",
            parent_id="post_001",
            agent_id="agent_local_demo",
            content="哈哈哈老外第一次来都会懵！你可以先去地铁站的服务窗口找工作人员帮忙开通，或者下载个「亿通行」APP，用护照就能注册~超简单的！",
            timestamp=datetime.now().isoformat()
        ),
        InteractionNode(
            node_id="reply_002",
            parent_id="reply_001",
            agent_id="agent_expat_demo",
            content="tbh 我当初也踩过这个坑！后来发现直接买交通卡最方便，不用实名，还能坐公交地铁~ 不用谢！",
            timestamp=datetime.now().isoformat()
        ),
        InteractionNode(
            node_id="reply_003",
            parent_id="reply_002",
            agent_id="agent_local_demo",
            content="对对对！交通卡真的绝绝子！充值也方便，地铁站自助机都能充~ 冲就完事了！",
            timestamp=datetime.now().isoformat()
        )
    ]

    payload = SocialDataPayload(
        post_id="demo_post_001",
        main_content=sample_interactions[0].content,
        location="北京",
        author_persona=sample_persona,
        interactions=sample_interactions,
        annotations={
            "sentiment": "anxious",
            "intent": "ask_for_help",
            "topic_tags": ["移动支付", "北京地铁", "外国游客", "交通出行"],
            "key_themes": ["支付困难", "文化交流", "本地建议"]
        }
    )

    print("\n[1] 生成的数据结构：")
    print(f"    帖子ID: {payload.post_id}")
    print(f"    作者人设: {payload.author_persona.role_type} - {payload.author_persona.nationality}")
    print(f"    地点: {payload.location}")
    print(f"    互动数: {len(payload.interactions)} 条")

    print("\n[2] 内容预览：")
    print("-" * 60)
    print(f"\n【主帖】by {sample_persona.nationality}游客\n{payload.main_content}\n")
    for i, interaction in enumerate(payload.interactions[1:], 1):
        role = "本地人" if "local" in interaction.agent_id else "外籍人士"
        print(f"【回复 {i}】by {role}\n{interaction.content}\n")

    print("[3] 标注结果（预填充）：")
    print(f"    情感: {payload.annotations.get('sentiment')}")
    print(f"    意图: {payload.annotations.get('intent')}")
    print(f"    话题标签: {', '.join(payload.annotations.get('topic_tags', []))}")

    print("\n[4] 导出数据集...")
    exporter = DatasetExporter()
    import asyncio
    raw_path = asyncio.run(exporter.asave_raw([payload]))
    alpaca_path = asyncio.run(exporter.asave_alpaca([payload]))
    sharegpt_path = asyncio.run(exporter.asave_sharegpt([payload]))

    print(f"\n[5] 导出完成:")
    print(f"    [OK] 原始数据: {raw_path}")
    print(f"    [OK] Alpaca格式: {alpaca_path}")
    print(f"    [OK] ShareGPT格式: {sharegpt_path}")

    print("\n" + "=" * 60)
    print("系统演示完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 复制 .env.example 为 .env")
    print("2. 填写你的 DeepSeek/Qwen API 密钥")
    print("3. 运行 'python main.py' 使用真实 API 生成数据")
    print("\n示例数据已导出到 ./output 目录！")


if __name__ == "__main__":
    main()
