"""
测试执行入口文件

本文件是API自动化测试框架的主入口，负责：
1. 执行pytest测试用例
2. 生成Allure和HTML测试报告
3. 保留历史记录，支持趋势图展示
4. 按执行时间保存每次的报告副本

使用方式：
    python run.py

方式2：指定环境运行
    set TEST_ENV=prod
    python run.py

输出报告：
    1. Allure HTML报告（最新）：bucket/allure-html/index.html
    2. HTML报告：bucket/html-report/report.html
    3. 历史记录：bucket/allure-history/
    4. 按时间归档的报告：bucket/allure-reports/YYYYMMDD_HHMMSS/
"""

import sys
import os
import shutil
from datetime import datetime

BUCKET_DIR = os.path.join(os.path.dirname(__file__), "bucket")


def prepare_allure_history(allure_dir: str, history_dir: str):
    """运行测试前，加载历史记录到 allure-results/history/"""
    if os.path.exists(history_dir):
        target_dir = os.path.join(allure_dir, "history")
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(history_dir, target_dir)
        print(f"✅ 已加载历史记录: {history_dir}")
    else:
        print(f"ℹ️ 历史记录目录不存在，跳过加载: {history_dir}")


def save_allure_history(allure_html_dir: str, history_dir: str):
    """生成报告后，保存历史记录到 allure-history/"""
    source_history = os.path.join(allure_html_dir, "history")
    if os.path.exists(source_history):
        if os.path.exists(history_dir):
            shutil.rmtree(history_dir)
        shutil.copytree(source_history, history_dir)
        print(f"✅ 已保存历史记录: {history_dir}")
    else:
        print(f"⚠️ 报告历史目录不存在: {source_history}")


def archive_allure_report(allure_html_dir: str, archive_base_dir: str):
    """按执行时间保存报告副本到归档目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, timestamp)

    if os.path.exists(allure_html_dir):
        shutil.copytree(allure_html_dir, archive_dir)
        print(f"✅ 已归档报告: {archive_dir}")
    else:
        print(f"⚠️ 报告目录不存在，跳过归档: {allure_html_dir}")


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    
    allure_results_dir = os.path.join(BUCKET_DIR, "allure-results")
    allure_report_dir = os.path.join(BUCKET_DIR, "allure-report")
    html_report_dir = os.path.join(BUCKET_DIR, "html-report")
    history_dir = os.path.join(BUCKET_DIR, "history")
    archive_dir = os.path.join(BUCKET_DIR, "archives")
    
    os.makedirs(allure_results_dir, exist_ok=True)
    os.makedirs(html_report_dir, exist_ok=True)

    prepare_allure_history(allure_results_dir, history_dir)
    
    print("\n" + "=" * 50)
    print("执行测试用例...")
    print("=" * 50)
    
    result = os.system(
        f'pytest src/testcases/ -v '
        f'--alluredir="{allure_results_dir}" '
        f'--html="{os.path.join(html_report_dir, "report.html")}" '
        f'--self-contained-html'
    )
    
    print("\n" + "=" * 50)
    print("生成测试报告...")
    print("=" * 50)
    
    os.system(f'allure generate "{allure_results_dir}" -o "{allure_report_dir}" --clean')

    save_allure_history(allure_report_dir, history_dir)
    archive_allure_report(allure_report_dir, archive_dir)

    print("\n" + "=" * 50)
    print("测试报告已生成:")
    print(f"✅ Allure报告: {os.path.abspath(allure_report_dir)}")
    print(f"✅ HTML报告: {os.path.abspath(os.path.join(html_report_dir, 'report.html'))}")
    print(f"✅ 历史记录: {os.path.abspath(history_dir)}")
    print(f"✅ 归档报告: {os.path.abspath(archive_dir)}")
    print("=" * 50)
    
    sys.exit(result)
