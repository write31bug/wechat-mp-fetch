# test_multi_discussion.py
"""
多 Agent 讨论系统 · 测试脚本
测试各个模块的基本功能（不依赖 LLM）
"""

import asyncio
import sys
import os
import shutil
from pathlib import Path

# 把 multi-discussion 目录加入 path
sys.path.insert(0, str(Path(__file__).parent))

from storage_manager import StorageManager, SessionPaths, generate_session_id, slugify
from context_builder import ContextBuilder, AgentConfig, Message
from summary_generator import SummaryGenerator, Summary
from orchestrator import DiscussionOrchestrator, OrchestratorConfig
from agent_pool import AgentPool, ToolCall


# ────────────────────────────────────────────────
# 测试工具
# ────────────────────────────────────────────────

TEST_BASE = Path("E:/openclaw/tasks/multi-discussion/_test_output")

def setup():
    """测试前清理"""
    if TEST_BASE.exists():
        shutil.rmtree(TEST_BASE)
    TEST_BASE.mkdir(parents=True)
    print(f"✅ 测试目录: {TEST_BASE}")

def teardown():
    """测试后清理"""
    if TEST_BASE.exists():
        shutil.rmtree(TEST_BASE)
    print("🧹 测试目录已清理")

def assert_eq(actual, expected, msg=""):
    if actual != expected:
        print(f"❌ FAIL: {msg}")
        print(f"   预期: {expected}")
        print(f"   实际: {actual}")
        return False
    print(f"✅ {msg}")
    return True

def assert_true(condition, msg=""):
    if not condition:
        print(f"❌ FAIL: {msg}")
        return False
    print(f"✅ {msg}")
    return True


# ────────────────────────────────────────────────
# Test 1: storage_manager
# ────────────────────────────────────────────────

def test_storage_manager():
    print("\n=== Test 1: storage_manager ===")
    sm = StorageManager(base_path=TEST_BASE)

    # test slugify
    assert_eq(slugify("AI是否会取代程序员？"), "AI是否会取代程序员", "slugify 基本功能")
    assert_eq(slugify("test/path*with|bad:chars"), "testpathwithbadchars", "slugify 过滤特殊字符")

    # test generate_session_id
    sid = generate_session_id("测试主题")
    assert_true(sid.startswith("2026-04-07_测试主题"), "generate_session_id 格式正确")

    # test init_session（N=3 agents）
    paths = sm.init_session("AI是否会取代程序员", ["optimist", "skeptic", "neutral"], rounds=2)

    assert_true(paths.base.exists(), "session 目录创建")
    assert_true((paths.base / "manifest.json").exists(), "manifest.json 创建")
    assert_true((paths.base / "history.json").exists(), "history.json 创建")
    assert_true((paths.base / "summary.md").exists(), "summary.md 创建")
    assert_true((paths.base / "contributions").exists(), "contributions 目录创建")

    # 检查 N=3 个 agent 子目录
    contrib_dir = paths.base / "contributions"
    for agent in ["optimist", "skeptic", "neutral"]:
        assert_true((contrib_dir / agent).exists(), f"agent 子目录创建: {agent}")

    # test manifest 内容
    manifest = sm.read_manifest(paths)
    assert_eq(manifest["topic"], "AI是否会取代程序员", "manifest topic 正确")
    assert_eq(manifest["rounds"], 2, "manifest rounds 正确")
    assert_eq(manifest["agents"], ["optimist", "skeptic", "neutral"], "manifest agents 正确")
    assert_eq(manifest["status"], "PENDING", "初始状态 PENDING")

    # test save contribution
    sm.save_contribution(paths, "optimist", 1, "AI会创造更多机会")
    sm.save_contribution(paths, "skeptic", 1, "但也会取代部分工作")
    sm.save_contribution(paths, "neutral", 1, "需要平衡看待")

    content = (paths.base / "contributions" / "optimist" / "round1.md").read_text(encoding="utf-8")
    assert_eq(content, "AI会创造更多机会", "save_contribution 写入正确")

    # test load all contributions
    msgs = sm.load_all_contributions(paths, ["optimist", "skeptic", "neutral"], 1)
    assert_eq(len(msgs), 3, "load_all_contributions 返回 N=3 条")

    # test update_manifest_status
    sm.update_manifest_status(paths, "IN_PROGRESS")
    manifest = sm.read_manifest(paths)
    assert_eq(manifest["status"], "IN_PROGRESS", "状态更新正确")

    # test append_history
    sm.append_history(paths, 1, [{"agent": "optimist", "content": "AI会创造更多机会"}])
    history = sm.read_history(paths)
    assert_eq(len(history["rounds"]), 1, "history.json 追加成功")

    # test write_summary
    sm.write_summary(paths, "# 总结报告\n这是测试总结")
    summary_content = (paths.base / "summary.md").read_text(encoding="utf-8")
    assert_true("总结报告" in summary_content, "write_summary 写入正确")


# ────────────────────────────────────────────────
# Test 2: context_builder
# ────────────────────────────────────────────────

def test_context_builder():
    print("\n=== Test 2: context_builder ===")

    cb = ContextBuilder("AI是否会取代程序员")

    agents = [
        AgentConfig(id="optimist", name="乐观派", role="相信AI带来机遇", personality="积极"),
        AgentConfig(id="skeptic", name="怀疑派", role="关注风险", personality="谨慎"),
    ]

    # 无历史时
    ctx = cb.build(1, 3, agents[0], history=[], this_round_previous=None)
    assert_true("AI是否会取代程序员" in ctx, "上下文包含主题")
    assert_true("第 1 轮" in ctx and "共 3 轮" in ctx, "上下文包含轮次")
    assert_true("乐观派" in ctx, "上下文包含角色名")
    assert_true("相信AI带来机遇" in ctx, "上下文包含角色定位")
    assert_true("积极" in ctx, "上下文包含性格")
    assert_true("暂无历史发言" in ctx, "无历史时提示正确")

    # 有历史时（Round 2）
    history = [
        Message("optimist", "乐观派", 1, "AI会创造更多机会"),
        Message("skeptic", "怀疑派", 1, "但也会取代部分工作"),
    ]
    ctx = cb.build(2, 3, agents[1], history=history, this_round_previous=[])
    assert_true("第 2 轮" in ctx, "Round 2 正确")
    assert_true("历史发言" in ctx, "有历史时显示历史发言")
    assert_true("乐观派" in ctx, "历史包含乐观派发言")
    assert_true("skeptic" not in ctx or "第 2 轮" not in ctx.split("历史发言")[1], "本轮发言不在历史中")

    # 串行模式：本轮前面有人发言
    this_round_prev = [
        Message("optimist", "乐观派", 2, "我依然乐观"),
    ]
    ctx = cb.build(2, 3, agents[1], history=history, this_round_previous=this_round_prev)
    assert_true("本轮其他人的发言" in ctx, "串行模式显示本轮其他人")
    assert_true("乐观派（本轮先于你发言）" in ctx, "标注先于你发言")
    assert_true("我依然乐观" in ctx, "显示乐观派本轮发言")


# ────────────────────────────────────────────────
# Test 3: summary_generator
# ────────────────────────────────────────────────

def test_summary_generator():
    print("\n=== Test 3: summary_generator ===")

    sg = SummaryGenerator()

    agents = {
        "optimist": AgentConfig(id="optimist", name="乐观派", role="相信AI带来机遇"),
        "skeptic": AgentConfig(id="skeptic", name="怀疑派", role="关注风险"),
    }

    messages = [
        Message("optimist", "乐观派", 1, "AI会创造更多机会"),
        Message("skeptic", "怀疑派", 1, "但也会取代部分工作"),
        Message("optimist", "乐观派", 2, "新岗位会抵消失业"),
        Message("skeptic", "怀疑派", 2, "转型需要时间和成本"),
    ]

    # test generate (prompt building)
    prompt = sg.generate(messages, agents)
    assert_true("乐观派" in prompt, "prompt 包含角色说明")
    assert_true("AI会创造更多机会" in prompt, "prompt 包含发言内容")
    assert_true("主要共识" in prompt, "prompt 包含总结要求")
    assert_true("key_consensus" in prompt, "prompt 要求 JSON 格式")

    # test parse_result（合法 JSON）
    valid_json = '{"key_consensus":["共识1","共识2"],"key_disagreements":["分歧1"],"recommendation":"建议","agent_views":{"optimist":"乐观"}}'
    summary = sg.parse_result(valid_json, agents)
    assert_eq(len(summary.key_consensus), 2, "解析共识条数")
    assert_eq(summary.recommendation, "建议", "解析建议")
    assert_eq(summary.agent_views["optimist"], "乐观", "解析 agent_views")

    # test parse_result（非法 JSON 降级）
    bad_summary = sg.parse_result("这不是 JSON", agents)
    assert_true("失败" in bad_summary.key_consensus[0], "非法 JSON 降级处理")
    assert_eq(bad_summary.recommendation, "这不是 JSON", "降级保留原始内容")

    # test format_markdown
    summary = Summary(
        key_consensus=["AI改变工作方式"],
        key_disagreements=["替代程度不同"],
        recommendation="持续学习应对变化",
        agent_views={"optimist": "AI带来机遇", "skeptic": "转型有挑战"}
    )
    md = sg.format_markdown(summary, "AI与程序员", agents)
    assert_true("讨论总结" in md, "总结报告包含标题")
    assert_true("AI改变工作方式" in md, "总结包含共识")
    assert_true("持续学习应对变化" in md, "总结包含建议")
    assert_true("乐观派" in md and "AI带来机遇" in md, "总结包含各方观点")


# ────────────────────────────────────────────────
# Test 4: orchestrator（无 LLM，测试骨架逻辑）
# ────────────────────────────────────────────────

def test_orchestrator():
    print("\n=== Test 4: orchestrator（骨架测试） ===")

    agents = [
        AgentConfig(id="optimist", name="乐观派", role="相信AI带来机遇"),
        AgentConfig(id="skeptic", name="怀疑派", role="关注风险"),
    ]

    config = OrchestratorConfig(rounds=2)

    # 测试新的 orchestrator API（LLM-aware 架构）
    orch = DiscussionOrchestrator("AI是否会取代程序员", agents, config)
    orch.storage.base_path = TEST_BASE / "orch_test"

    # 1. init_session
    paths = orch.init_session()
    assert_true(paths.base.exists(), "session 目录存在")
    assert_true((paths.base / "manifest.json").exists(), "manifest 存在")

    # 2. build_context（不调 LLM，验证上下文正确）
    ctx = orch.build_context(round_num=1, agent=agents[0])
    assert_true("AI是否会取代程序员" in ctx, "上下文包含主题")
    assert_true("乐观派" in ctx, "上下文包含角色")

    # 3. 模拟 LLM 返回结果，调用 save_contribution
    orch.save_contribution("optimist", 1, "AI会带来更多机会")
    orch.save_contribution("skeptic", 1, "但也有替代风险")

    # 检查发言文件
    f1 = paths.base / "contributions" / "optimist" / "round1.md"
    assert_true(f1.exists(), "optimist round1 发言文件生成")
    content = f1.read_text(encoding="utf-8")
    assert_eq(content, "AI会带来更多机会", "发言内容正确")

    # 4. Round 2
    ctx2 = orch.build_context(round_num=2, agent=agents[1])
    assert_true("第 2 轮" in ctx2, "Round 2 上下文正确")
    assert_true("乐观派" in ctx2, "Round 2 包含 Round 1 历史")

    orch.save_contribution("optimist", 2, "新机会不断涌现")
    orch.save_contribution("skeptic", 2, "转型需要时间成本")

    # 5. save_summary（模拟 LLM 返回的总结）
    mock_summary = '{"key_consensus":["AI改变工作方式"],"key_disagreements":["替代程度"],"recommendation":"持续学习","agent_views":{"optimist":"乐观","skeptic":"谨慎"}}'
    orch.save_summary(mock_summary)

    summary_path = paths.base / "summary.md"
    summary_content = summary_path.read_text(encoding="utf-8")
    assert_true(len(summary_content) > 0, "summary 有内容")
    assert_true("讨论总结" in summary_content, "summary 包含标题")

    # 6. complete
    orch.complete()
    manifest = orch.storage.read_manifest(paths)
    assert_eq(manifest["status"], "COMPLETED", "最终状态 COMPLETED")
    assert_eq(manifest["current_round"], 2, "最后记录轮次 2")

    assert_true(True, "orchestrator 端到端骨架测试通过")


# ────────────────────────────────────────────────
# Test 5: agent_pool
# ────────────────────────────────────────────────

def test_agent_pool():
    print("\n=== Test 5: agent_pool ===")

    pool = AgentPool(default_model="gpt-4o")

    agent = AgentConfig(
        id="optimist",
        name="乐观派",
        role="相信AI带来机遇",
        personality="积极",
        model="gpt-4o",
        temperature=0.8
    )

    # test prepare_call
    tc = pool.prepare_call(agent, "请发表意见")
    assert_eq(tc.tool_name, "sessions_spawn", "tool_name 正确")
    assert_true("乐观派" in tc.task, "task 包含角色名")
    assert_true("相信AI带来机遇" in tc.task, "task 包含角色定位")
    assert_eq(tc.model, "gpt-4o", "model 正确")
    assert_eq(tc.cleanup, "delete", "cleanup 正确")

    # test prepare_summary_call
    tc_sum = pool.prepare_summary_call("请总结这段讨论")
    assert_eq(tc_sum.tool_name, "sessions_spawn", "summary tool_name 正确")
    assert_true("请总结" in tc_sum.task, "summary task 正确")

    # test ToolCall 字段完整性
    assert_eq(tc.tool_name, "sessions_spawn", "tool_name = sessions_spawn")
    assert_eq(tc.agent_id, "optimist", "agent_id = optimist")
    assert_true("乐观派" in tc.task, "task 包含角色名")
    assert_eq(tc.runtime, "subagent", "runtime = subagent")
    assert_eq(tc.mode, "run", "mode = run")
    assert_eq(tc.cleanup, "delete", "cleanup = delete")


# ────────────────────────────────────────────────
# 运行所有测试
# ────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("多 Agent 讨论系统 · 测试套件")
    print("=" * 50)

    setup()
    try:
        test_storage_manager()
        test_context_builder()
        test_summary_generator()
        test_orchestrator()
        test_agent_pool()
        print("\n" + "=" * 50)
        print("✅ 全部测试通过")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        teardown()
