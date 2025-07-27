#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片使用场景分析器
通过分析图片分辨率和比例，识别适用场景：PC、平板、手机、头像等
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
from typing import Dict, List


class ImageSceneAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图片使用场景分析器")
        self.root.geometry("800x700")
        self.root.configure(bg="#fafafa")
        ttk.Style().theme_use("clam")
        self.colors = {
            "bg": "#fafafa",
            "card": "#ffffff",
            "accent": "#4f46e5",  # 主色
            "accent2": "#10b981",  # 辅色
            "text": "#111827",
            "text2": "#6b7280",
            "red": "#ef4444",
        }

        # 场景标准比例
        self.scene_ratios = {
            "头像": [(1, 1)],  # 正方形
            "手机": [(9, 16), (9, 18), (9, 19.5), (10, 16), (2, 3)],  # 手机比例
            "平板": [(4, 3), (16, 10), (3, 2), (5, 4)],  # 平板比例
            "PC": [(16, 9), (21, 9), (16, 10), (4, 3), (5, 4), (3, 2)],  # PC比例
        }

        # 容差范围
        self.tolerance = 0.05

        self.analysis_results = {}
        self.current_image_path = None

        self.setup_ui()

    def setup_ui(self):
        # ---------- 配色 ----------
        self.colors = {
            "bg": "#fafafa",
            "canvas": "#f3f4f6",  # 左侧预览区背景
            "text": "#374151",
            "card": ["#e0e7ff", "#e0f2fe", "#fce7f3", "#fef3c7"],
        }

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background=self.colors["bg"])
        style.configure(
            "Accent.TButton",
            background="#6366f1",
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Accent.TButton", background=[("active", "#4f46e5")])

        # ---------- 布局 ----------
        main = ttk.Frame(self.root, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # 顶部按钮
        top = ttk.Frame(main, style="Main.TFrame")
        top.pack(fill="x", pady=(0, 15))
        ttk.Button(
            top, text=" 选择图片", style="Accent.TButton", command=self.select_image
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            top, text=" 批量分析", style="Accent.TButton", command=self.batch_analyze
        ).pack(side="left")

        # ---------- 内容区 ----------
        body = ttk.Frame(main, style="Main.TFrame")
        body.pack(fill="both", expand=True)

        # 左侧
        self.canvas = tk.Canvas(body, bg=self.colors["canvas"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 15))
        self.canvas.bind("<Configure>", self._redraw_canvas)
        self.canvas.bind(
            "<Button-1>", lambda e: self.select_image()
        )  # 容器绑定选择图片功能

        # 右侧
        self.result_card = tk.Frame(body, bg=self.colors["bg"])
        self.result_card.pack(side="left", fill="both", expand=True)

        # 标题
        tk.Label(
            self.result_card,
            text=" 分析结果",
            font=("Segoe UI", 15, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
        ).pack(anchor="w")

    def _redraw_canvas(self, event=None):
        self.canvas.delete("all")
        cvs_w, cvs_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cvs_w <= 1 or cvs_h <= 1:
            return

        # 加载提示
        self.canvas.create_text(
            cvs_w // 2,
            cvs_h // 2,
            text="加载中…",
            fill="#4f46e5",
            font=("Segoe UI", 14, "bold"),
        )
        self.canvas.update_idletasks()  # 刷新

        if not self.current_image_path:  # 空状态
            # 渐变背景
            for i in range(0, cvs_h, 2):
                color = self._interpolate_color("#e0e7ff", "#f3f4f6", i / cvs_h)
                self.canvas.create_line(0, i, cvs_w, i, fill=color, width=2)

            # 居中插画
            cx, cy = cvs_w // 2, cvs_h // 2
            r = min(cvs_w, cvs_h) // 8
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r, outline="#a5b4fc", width=3
            )
            self.canvas.create_line(
                cx - r // 2, cy, cx + r // 2, cy, fill="#a5b4fc", width=3
            )
            self.canvas.create_line(
                cx, cy - r // 2, cx, cy + r // 2, fill="#a5b4fc", width=3
            )
            self.canvas.create_text(
                cx,
                cy + r + 30,
                text="点击上传图片",
                fill="#6b7280",
                font=("Segoe UI", 12),
            )
            return

        # 图片绘制
        img = Image.open(self.current_image_path)
        img_w, img_h = img.size
        scale = max(cvs_w / img_w, cvs_h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        x, y = (cvs_w - new_w) // 2, (cvs_h - new_h) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.tk_img)

    def _interpolate_color(self, c1, c2, t):
        """线性插值十六进制颜色"""
        c1 = tuple(int(c1[i : i + 2], 16) for i in (1, 3, 5))
        c2 = tuple(int(c2[i : i + 2], 16) for i in (1, 3, 5))
        r = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        return f"#{r[0]:02x}{r[1]:02x}{r[2]:02x}"

    def select_image(self):
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
        ]

        file_path = filedialog.askopenfilename(title="选择文件", filetypes=file_types)

        if file_path:
            self.load_and_analyze_image(file_path)

    def batch_analyze(self):
        """批量分析图片"""
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if not folder_path:
            return

        # 支持的图片格式
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

        # 获取文件夹中的所有图片文件
        image_files = []
        for filename in os.listdir(folder_path):
            if os.path.splitext(filename.lower())[1] in image_extensions:
                image_files.append(os.path.join(folder_path, filename))

        if not image_files:
            messagebox.showwarning("提示", "所选文件夹中没有找到图片！")
            return

        # 批量分析
        results_summary = []
        for image_path in image_files:
            try:
                analysis = self.analyze_image(image_path)
                filename = os.path.basename(image_path)
                results_summary.append(f"{filename}: {analysis['best_scene']}")
            except Exception as e:
                filename = os.path.basename(image_path)
                results_summary.append(f"{filename}: 分析失败 - {str(e)}")

        # 显示批量分析结果
        self.show_batch_results(results_summary)

    def show_batch_results(self, results: List[str]):
        """显示批量分析结果"""
        result_window = tk.Toplevel(self.root)
        result_window.title("分析结果")
        result_window.geometry("600x400")
        result_window.configure(bg="#f0f0f0")

        # 创建文本框显示结果
        text_frame = tk.Frame(result_window, bg="#f0f0f0")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 插入结果
        for result in results:
            text_widget.insert(tk.END, result + "\n")

        text_widget.config(state=tk.DISABLED)

    def load_and_analyze_image(self, image_path: str):
        """加载并分析图片"""
        try:
            # 分析图片
            self.analysis_results = self.analyze_image(image_path)

            # 更新预览
            self.update_image_preview(image_path)

            # 显示分析结果
            self.display_results()

        except Exception as e:
            messagebox.showerror("错误", f"处理时发生错误: {str(e)}")

    def analyze_image(self, image_path: str) -> Dict:
        """分析图片场景适用性"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            raise Exception(f"无法打开文件: {str(e)}")

        # 图片比例
        image_ratio = width / height

        # 分析各个场景的适用性
        scene_analysis = {}
        suitable_scenes = []

        for scene_name, ratios in self.scene_ratios.items():  # 枚举所有标准比例
            is_suitable = False
            best_match_ratio = None
            min_difference = float("inf")

            for standard_w, standard_h in ratios:
                standard_ratio = standard_w / standard_h
                # 差异度：图片比例 - 标准比例 / 标准比例
                difference = abs(image_ratio - standard_ratio) / standard_ratio

                if difference < min_difference:
                    min_difference = difference
                    best_match_ratio = f"{standard_w}:{standard_h}"

                # 检查是否在容差范围内
                if difference <= self.tolerance:
                    is_suitable = True  # 该场景适用

            scene_analysis[scene_name] = {
                "suitable": is_suitable,
                "difference": min_difference,
                "best_match_ratio": best_match_ratio,
                "distortion_level": self.get_distortion_level(min_difference),
            }

            if is_suitable:
                suitable_scenes.append(scene_name)

        # 确定最佳场景
        if suitable_scenes:
            # 选择差异最小的适用场景
            best_scene = min(
                suitable_scenes, key=lambda x: scene_analysis[x]["difference"]
            )
        else:
            best_scene = "其他"

        return {
            "width": width,
            "height": height,
            "ratio": image_ratio,
            "scene_analysis": scene_analysis,
            "suitable_scenes": suitable_scenes,
            "best_scene": best_scene,
            "path": image_path,
        }

    def get_distortion_level(self, difference: float) -> str:
        """根据差异程度返回变形级别"""
        if difference <= 0.02:
            return "无变形"
        elif difference <= 0.05:
            return "轻微变形"
        elif difference <= 0.10:
            return "中等变形"
        elif difference <= 0.20:
            return "明显变形"
        else:
            return "严重变形"

    def update_image_preview(self, image_path: str):
        """Canvas 重绘图片"""
        try:
            with Image.open(image_path):
                pass
        except Exception as e:
            # 清空画布，显示错误提示
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text=f"预览失败: {str(e)}",
                fill="#ef4444",
                font=("Segoe UI", 12),
            )
            return

        # 记录路径，进行重绘
        self.current_image_path = image_path
        self._redraw_canvas()

    def display_results(self):
        if not self.analysis_results:
            return

        self.current_image_path = self.analysis_results.get("path")  # 记录路径
        self._redraw_canvas()

        # 清空旧卡片
        for w in self.result_card.winfo_children()[1:]:
            w.destroy()

        res = self.analysis_results
        scenes = list(res["scene_analysis"].items())
        for idx, (scene, info) in enumerate(scenes):
            bg = self.colors["card"][idx % len(self.colors["card"])]
            card = tk.Frame(self.result_card, bg=bg, height=80, bd=0)
            card.pack(fill="x", pady=6)
            card.pack_propagate(False)

            icon = {"手机": "📱", "PC": "💻", "平板": "📟", "头像": "👤"}.get(scene, "")
            txt = f"{icon} {scene}"
            if info["suitable"]:
                txt += "  ·  适配"
            else:
                txt += "  ·  不适配"
            tk.Label(
                card,
                text=txt,
                font=("Segoe UI", 12, "bold"),
                bg=bg,
                fg=self.colors["text"],
            ).pack(side="left", padx=15, pady=10)

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = ImageSceneAnalyzer()
        app.run()
    except Exception as e:
        print(f"应用程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
