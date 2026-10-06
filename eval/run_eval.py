import json
import os
import sys
import requests
import time

BASE_URL = "http://localhost:8000"

def run_evaluation():
    questions_file = "./eval/questions.jsonl"
    if not os.path.exists(questions_file):
        print(f"Error: {questions_file} not found.")
        return

    results = []
    correct_type_count = 0
    total_count = 0

    with open(questions_file, "r") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            total_count += 1
            
            headers = {}
            if "my" in item["question"].lower() or "what if" in item["question"].lower():
                headers["X-Student-Id"] = "HCL2026-8891"

            payload = {"question": item["question"]}
            
            start_time = time.time()
            try:
                res = requests.post(f"{BASE_URL}/ask", headers=headers, json=payload, timeout=10)
                resp_json = res.json()
                latency = round((time.time() - start_time) * 1000, 2)
            except Exception as err:
                resp_json = {"answer": "Error", "answer_type": "error", "trace_id": "ERR"}
                latency = round((time.time() - start_time) * 1000, 2)

            expected_type = item["expected_answer_type"]
            actual_type = resp_json.get("answer_type", "unknown")
            is_type_match = (expected_type == actual_type)
            if is_type_match:
                correct_type_count += 1

            results.append({
                "id": item["id"],
                "question": item["question"],
                "expected_answer_type": expected_type,
                "actual_answer_type": actual_type,
                "type_match": is_type_match,
                "actual_answer": resp_json.get("answer"),
                "citations_count": len(resp_json.get("citations", [])),
                "verified": item.get("verified", False),
                "trace_id": resp_json.get("trace_id"),
                "latency_ms": latency
            })

    accuracy_pct = round((correct_type_count / total_count) * 100, 2) if total_count > 0 else 0.0

    eval_summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": total_count,
        "type_match_accuracy_pct": accuracy_pct,
        "results": results
    }

    os.makedirs("./docs/debug", exist_ok=True)
    with open("./docs/debug/eval_results_initial.json", "w") as out_f:
        json.dump(eval_summary, out_f, indent=2)

    print(f"Evaluation Complete: {correct_type_count}/{total_count} answer_type matches ({accuracy_pct}%). Saved to docs/debug/eval_results_initial.json")

if __name__ == '__main__':
    run_evaluation()
