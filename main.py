
import asyncio
from dotenv import load_dotenv
from src.agents.graph_workflow import CommunityInteractionGraph
from src.core.evaluator import EvaluationLoop
from src.core.annotator import AutoAnnotator
from src.data.dataset_exporter import DatasetExporter

load_dotenv()


async def main():
    print("=" * 50)
    print("子网页智能体数据生成与标注系统")
    print("=" * 50)

    scenario = "外国游客在北京地铁使用移动支付遇到困难，发现自己没有本地朋友求助"
    location = "北京"

    print(f"\n场景: {scenario}")
    print(f"地点: {location}\n")

    graph = CommunityInteractionGraph(llm_provider="deepseek")
    evaluation_loop = EvaluationLoop(max_retries=3)
    annotator = AutoAnnotator()
    exporter = DatasetExporter()

    print("正在生成社交互动内容...")
    payload, report = await evaluation_loop.arun_with_evaluation(
        graph.arun,
        scenario,
        location
    )

    print(f"\n评估结果:")
    print(f"  拟人度: {report.human_likeness_score}")
    print(f"  连贯性: {report.coherence_score}")
    print(f"  是否通过: {'是' if report.is_passed else '否'}")
    print(f"  重试次数: {report.retry_count}")
    print(f"  反馈: {report.feedback}")

    print("\n正在进行自动标注...")
    payload = await annotator.aannotate(payload)

    print(f"\n标注结果:")
    print(f"  情感: {payload.annotations.get('sentiment')}")
    print(f"  意图: {payload.annotations.get('intent')}")
    print(f"  话题标签: {', '.join(payload.annotations.get('topic_tags', []))}")

    print("\n正在导出数据集...")
    raw_path = await exporter.asave_raw([payload])
    alpaca_path = await exporter.asave_alpaca([payload])
    sharegpt_path = await exporter.asave_sharegpt([payload])

    print(f"\n导出完成:")
    print(f"  原始数据: {raw_path}")
    print(f"  Alpaca格式: {alpaca_path}")
    print(f"  ShareGPT格式: {sharegpt_path}")

    print("\n" + "=" * 50)
    print("生成的内容预览:")
    print("=" * 50)
    print(f"【主帖】\n{payload.main_content}\n")
    for i, interaction in enumerate(payload.interactions[1:], 1):
        print(f"【回复 {i}】\n{interaction.content}\n")


if __name__ == "__main__":
    asyncio.run(main())
