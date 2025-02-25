# main.py
from utils import *
from config import *

def research_workflow(topic):
    # 阶段1：需求解析
    research_plan = llm_analyze(
        prompt=f"将研究主题「{topic}」分解为5-7个关键研究维度，生成初步研究框架，以列表形式返回。"
    )
    print("研究计划：", research_plan)
    # 假设LLM返回的是一个Python列表格式的字符串，我们需要将其解析为列表
    try:
        research_plan = eval(research_plan)  # 注意：eval存在安全风险，如果LLM的输出不可控，应使用更安全的方法
    except Exception as e:
        print(f"解析研究计划出错: {e}，使用默认维度。")
        research_plan = ["市场规模", "竞争格局", "技术趋势", "用户需求", "政策法规"]

    all_data = {}

    # 阶段2：动态搜索分析
    for dimension in research_plan:
        print(f"开始研究维度：{dimension}")
        all_data[dimension] = ""
        retries = 3  # 设置重试次数
        while retries > 0:
            # 智能生成搜索关键词
            keywords = generate_keywords(dimension)
            print(f"  关键词：{keywords}")

            # 执行网页搜索
            search_results = duckduckgo_search(keywords, max_results=SEARCH_RESULT_COUNT)
            if not search_results:
                print("  没有搜索结果，减少关键词数量或更换关键词。")
                retries -= 1
                time.sleep(2)  # 等待一段时间再重试
                continue

            # 信息清洗与摘要生成
            cleaned_data = process_data(search_results)
            if not cleaned_data:
                print("  数据清洗失败，跳过此轮搜索。")
                retries -= 1
                time.sleep(2)
                continue

            # 信息可信度评估
            for result in search_results:
                credibility = assess_credibility(result['url'])
                print(f"  来源：{result['url']}，可信度：{credibility}")

            # 数据时效性验证
            recency = check_data_recency(cleaned_data)
            print(f"  数据时效性：{recency}")

            # 信息矛盾检测
            contradictions = detect_contradictions(cleaned_data)
            if contradictions:
                print("  检测到信息矛盾：")
                for c1, c2 in contradictions:
                    print(f"    - {c1}\n    - {c2}")

            # LLM分析评估
            analysis_prompt = "评估当前信息是否足够支撑该维度的研究，识别信息缺口，并以JSON格式返回结果，包含'sufficient' (bool)和'suggested_keywords' (list)两个字段。"
            analysis = llm_validate(
                context=cleaned_data,
                prompt=analysis_prompt
            )
            print("  LLM分析结果：", analysis)

            # 动态决策是否继续搜索
            if analysis and analysis.get("sufficient"):
                all_data[dimension] = cleaned_data
                break
            else:
                if analysis and analysis.get("suggested_keywords"):
                    keywords.extend(analysis["suggested_keywords"])
                retries -= 1
                time.sleep(2)  # 等待一段时间再重试

        if retries == 0:
            print(f"  达到最大重试次数，跳过维度「{dimension}」。")

    # 阶段3：知识图谱构建
    knowledge_graph = build_knowledge_graph(all_data)
    print("知识图谱：", knowledge_graph)

    # 阶段4：迭代式报告生成
    report = initialize_report()
    report["title"] = f"{topic} 市场调研报告"
    report["introduction"] = llm_analyze(prompt=f"为「{topic}」市场调研报告撰写引言。")

    for dimension, data in knowledge_graph.items():
        draft = llm_generate_section(data)
        report = integrate_content(report, draft)

        # 实时验证机制
        validation_prompt = "检查当前章节是否存在数据缺失或逻辑漏洞，并以JSON格式返回结果，包含'needs_search' (bool)和'search_clues' (list)两个字段。"
        validation = llm_validate(
            context=json.dumps(report['sections'], ensure_ascii=False),  # 传递当前所有章节的内容
            prompt=validation_prompt
        )

        if validation and validation.get("needs_search"):
            supplementary_search(validation["search_clues"])

    report["conclusion"] = llm_analyze(prompt=f"根据报告内容，为「{topic}」市场调研报告撰写结论。")

    # 添加参考文献（这里只是一个示例，实际应用中需要更完善的参考文献管理）
    for result in search_results:
        report["references"].append(f"{result['title']} - {result['url']}")

    # 最终质量审查
    final_report = quality_check(report)
    return final_report

if __name__ == "__main__":
    topic = input("请输入研究主题：")
    final_report = research_workflow(topic)
    print("\n最终报告：", final_report)

    # 生成PDF报告
    generate_pdf_report(final_report)
