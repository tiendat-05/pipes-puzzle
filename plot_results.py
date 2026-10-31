"""Vẽ ba biểu đồ so sánh từ benchmark_summary.json. Chạy: python plot_results.py"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

JSON_FILE = "benchmark_summary.json"

# Màu và nhãn hiển thị cho từng cấu hình giải thuật.
COLORS = {
    "dfs": "#2980b9",
    "astar": "#e67e22",
    "astar_old": "#95a5a6",
}
PRETTY = {
    "dfs": "Blind Search (DFS)",
    "astar": "Heuristic Search (A*)",
    "astar_old": "A* không tie-break",
}


def load_data(path=JSON_FILE):
    """Đọc số liệu đo đạc; báo lỗi rõ ràng nếu thiếu tệp."""
    if not os.path.exists(path):
        sys.exit(
            f"LỖI: không tìm thấy '{path}'.\n"
            f"Hãy chạy 'python run_experiments.py' trước để sinh số liệu."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_series(data):
    if "algos" in data:
        keys = [k for k in ("dfs", "astar", "astar_old") if k in data["algos"]]
        return keys, lambda key, metric: data["algos"][key][metric]

    mapping = {
        "dfs": ("dfs_time", "dfs_mem", "dfs_nodes"),
        "astar": ("astar_time", "astar_mem", "astar_nodes"),
    }
    metric_idx = {"time": 0, "mem": 1, "nodes": 2}

    def getter(key, metric):
        return data[mapping[key][metric_idx[metric]]]

    return list(mapping.keys()), getter


def grouped_bar(x, test_names, series_data, colors, title, ylabel, outfile,
                fmt="{:.2f}"):
    plt.figure(figsize=(9, 5.5))

    n_bars = len(series_data)
    width = 0.8 / n_bars
    offset = -0.4 + width / 2
    max_val = max(max(vals) for _name, vals, _color in series_data) or 1

    for i, (name, vals, color) in enumerate(series_data):
        rects = plt.bar(x + offset + i * width, vals, width, label=name,
                        color=color)
        for rect in rects:
            h = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2.0,
                     h + max_val * 0.015, fmt.format(h),
                     ha="center", va="bottom", fontsize=8)

    plt.title(title, fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Kích thước bàn cờ", fontsize=11)
    plt.ylabel(ylabel, fontsize=11)
    plt.xticks(x, test_names, fontsize=10)
    plt.legend(fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    print(f"-> Đã xuất: {outfile}")


def main():
    try:
        from pipes_solver import enable_utf8_stdout
        enable_utf8_stdout()
    except Exception:
        pass

    data = load_data()
    test_names = data["sizes"]
    solution_steps = data["steps"]
    keys, get_metric = build_series(data)

    x = np.arange(len(test_names))

    def series_for(metric):
        return [(PRETTY.get(k, k), get_metric(k, metric), COLORS.get(k, None))
                for k in keys]

    grouped_bar(x, test_names, series_for("time"),
                None,
                "So sánh Thời gian Thực thi Trung bình (5 Inputs/Size)",
                "Thời gian trung bình (ms)",
                "time_comparison.png")

    grouped_bar(x, test_names, series_for("mem"),
                None,
                "So sánh Bộ nhớ Đỉnh Trung bình (Peak RAM - KB)",
                "Bộ nhớ tiêu tốn trung bình (KB)",
                "memory_comparison.png",
                fmt="{:.1f}")

    node_data = series_for("nodes")
    plt.figure(figsize=(9, 5.5))
    n_bars = len(node_data)
    width = 0.8 / n_bars
    offset = -0.4 + width / 2
    max_val = max(max(vals) for _n, vals, _c in node_data) or 1

    for i, (name, vals, color) in enumerate(node_data):
        rects = plt.bar(x + offset + i * width, vals, width, label=name,
                        color=color)
        for rect in rects:
            h = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2.0,
                     h + max_val * 0.015, f"{h:.0f}",
                     ha="center", va="bottom", fontsize=8)

    plt.plot(x, solution_steps, color="#c0392b", marker="o", linewidth=2.5,
             label="Độ dài lời giải (số ô)")

    plt.title("Số Node Mở rộng Trung bình & Độ dài Lời giải",
              fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Kích thước bàn cờ", fontsize=11)
    plt.ylabel("Số lượng (Nodes / Ô)", fontsize=11)
    plt.xticks(x, test_names, fontsize=10)
    plt.legend(fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("nodes_comparison.png", dpi=300)
    plt.close()
    print("-> Đã xuất: nodes_comparison.png")


if __name__ == "__main__":
    main()
