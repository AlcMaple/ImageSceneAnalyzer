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

        self.scene_ratios = {
            "头像": [(1, 1)],
            "手机": [(9, 16), (9, 18), (9, 19.5), (10, 16), (2, 3)],
            "平板": [(4, 3), (16, 10), (3, 2), (5, 4)],
            "PC": [(16, 9), (21, 9), (16, 10), (4, 3), (5, 4), (3, 2)],
        }
        self.scene_min_resolution = {
            "头像": (300, 300),
            "手机": (1920, 1080),
            "平板": (1920, 1200),
            "PC": (1920, 1080),
        }
        self.tolerance = 0.05

        self.analysis_results = {}
        self.current_image_path = None
        self.current_layout = None

        self.setup_ui()

    def setup_ui(self):
        self.colors = {
            "bg": "#fafafa",
            "canvas": "#fafafa",
            "text": "#374151",
            "text_light": "#6b7280",
            "card": ["#e0e7ff", "#d1fae5", "#fee2e2", "#fef3c7"],
            "green": "#10b981",
            "red": "#ef4444",
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

        main = ttk.Frame(self.root, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        top = ttk.Frame(main, style="Main.TFrame")
        top.pack(fill="x", pady=(0, 15))
        ttk.Button(
            top, text=" 选择图片", style="Accent.TButton", command=self.select_image
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            top, text=" 批量分析", style="Accent.TButton", command=self.batch_analyze
        ).pack(side="left")

        self.body = ttk.Frame(main, style="Main.TFrame")
        self.body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            self.body, bg=self.colors["canvas"], highlightthickness=0
        )
        self.result_frame = tk.Frame(self.body, bg=self.colors["bg"])
        tk.Label(
            self.result_frame,
            text=" 分析结果",
            font=("Segoe UI", 15, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
        ).pack(anchor="w")
        self.result_card_container = tk.Frame(self.result_frame, bg=self.colors["bg"])
        self.result_card_container.pack(fill="both", expand=True)

        self._update_layout("side")
        self.canvas.bind("<Configure>", self._redraw_canvas)
        self.canvas.bind("<Button-1>", lambda e: self.select_image())

    def _update_layout(self, mode: str):
        if mode == self.current_layout:
            return
        self.canvas.pack_forget()
        self.result_frame.pack_forget()
        if mode == "bottom":
            self.canvas.pack(side="top", fill="both", expand=True, pady=(0, 15))
            self.result_frame.pack(side="top", fill="x", expand=False)
        else:
            self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 15))
            self.result_frame.pack(side="left", fill="both", expand=True)
        self.current_layout = mode

    def _redraw_canvas(self, event=None):
        self.canvas.delete("all")
        cvs_w, cvs_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cvs_w <= 1 or cvs_h <= 1:
            return

        if not self.current_image_path:
            self.canvas.configure(bg=self.colors["canvas"])
            for i in range(0, cvs_h, 2):
                color = self._interpolate_color("#e0e7ff", "#f3f4f6", i / cvs_h)
                self.canvas.create_line(0, i, cvs_w, i, fill=color, width=2)
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
        else:
            self.canvas.configure(bg=self.colors["canvas"])
            try:
                img = Image.open(self.current_image_path)
                img.thumbnail((cvs_w, cvs_h), Image.Resampling.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(img)
                x, y = (cvs_w - self.tk_img.width()) // 2, (
                    cvs_h - self.tk_img.height()
                ) // 2
                self.canvas.create_image(x, y, anchor="nw", image=self.tk_img)
            except Exception:
                self.canvas.create_text(
                    cvs_w // 2,
                    cvs_h // 2,
                    text="无法预览图片",
                    fill=self.colors["red"],
                    font=("Segoe UI", 14, "bold"),
                )

    def _interpolate_color(self, c1, c2, t):
        c1 = tuple(int(c1[i : i + 2], 16) for i in (1, 3, 5))
        c2 = tuple(int(c2[i : i + 2], 16) for i in (1, 3, 5))
        r = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        return f"#{r[0]:02x}{r[1]:02x}{r[2]:02x}"

    def select_image(self):
        file_types = [("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=file_types)
        if file_path:
            self.load_and_analyze_image(file_path)

    def load_and_analyze_image(self, image_path: str):
        try:
            self.analysis_results = self.analyze_image(image_path)
            new_layout = (
                "bottom" if self.analysis_results.get("best_scene") == "PC" else "side"
            )
            self._update_layout(new_layout)
            self.update_image_preview(image_path)
            self.display_results()
        except Exception as e:
            messagebox.showerror("错误", f"处理时发生错误: {str(e)}")
            self.current_image_path = None
            self._update_layout("side")
            self._redraw_canvas()

    def analyze_image(self, image_path: str) -> Dict:
        """
        分析图片场景适用性（综合考量比例和分辨率）
        对“手机”场景采用更灵活的特殊逻辑
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            raise Exception(f"无法打开文件: {str(e)}")

        img_long, img_short = max(width, height), min(width, height)
        scene_analysis = {}
        suitable_scenes = []

        for scene_name, ratios in self.scene_ratios.items():
            is_ratio_suitable = False
            is_resolution_suitable = False
            is_suitable = False
            best_match_ratio = "N/A"
            distortion_level = "N/A"
            min_difference = float("inf")

            if scene_name == "手机":
                # --- 手机壁纸的判断逻辑 ---
                if height > width:  # 竖屏图
                    portrait_ratio = width / height  # 计算实际比例
                    # 竖屏比例范围 (从9:21到9:14)
                    if 0.42 <= portrait_ratio <= 0.65:
                        is_ratio_suitable = True

                # 分辨率判断
                if img_short >= 1080 and img_long >= 1600:
                    is_resolution_suitable = True

                best_match_ratio = "竖屏壁纸"
                distortion_level = "几乎无" if is_ratio_suitable else "不适用"

            else:
                # --- 其他场景的通用判断逻辑 ---
                image_ratio = width / height
                for standard_w, standard_h in ratios:
                    standard_ratio = standard_w / standard_h
                    difference = abs(image_ratio - standard_ratio) / standard_ratio
                    if difference < min_difference:
                        min_difference = difference
                        best_match_ratio = f"{standard_w}:{standard_h}"

                if min_difference <= self.tolerance:
                    is_ratio_suitable = True

                min_long_req, min_short_req = self.scene_min_resolution.get(
                    scene_name, (0, 0)
                )
                if img_long >= min_long_req and img_short >= min_short_req:
                    is_resolution_suitable = True

                distortion_level = self.get_distortion_level(min_difference)

            # 最终适用性
            is_suitable = is_ratio_suitable and is_resolution_suitable

            scene_analysis[scene_name] = {
                "suitable": is_suitable,
                "ratio_suitable": is_ratio_suitable,
                "resolution_suitable": is_resolution_suitable,
                "difference": min_difference,
                "best_match_ratio": best_match_ratio,
                "distortion_level": distortion_level,
            }
            if is_suitable:
                suitable_scenes.append(scene_name)

        if suitable_scenes:
            if "手机" in suitable_scenes:
                best_scene = "手机"
            else:
                best_scene = min(
                    suitable_scenes, key=lambda x: scene_analysis[x]["difference"]
                )
        else:
            best_scene = "其他"

        return {
            "width": width,
            "height": height,
            "ratio": width / height,
            "scene_analysis": scene_analysis,
            "suitable_scenes": suitable_scenes,
            "best_scene": best_scene,
            "path": image_path,
        }

    def display_results(self):
        if not self.analysis_results:
            return
        for w in self.result_card_container.winfo_children():
            w.destroy()

        info_frame = tk.Frame(self.result_card_container, bg=self.colors["bg"])
        info_frame.pack(fill="x", pady=(5, 15))
        res_text = (
            f"{self.analysis_results['width']} x {self.analysis_results['height']}px"
        )
        tk.Label(
            info_frame,
            text=res_text,
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["text_light"],
        ).pack(side="left")

        res = self.analysis_results
        scenes = list(res["scene_analysis"].items())
        for idx, (scene, info) in enumerate(scenes):
            bg = self.colors["card"][idx % len(self.colors["card"])]
            card = tk.Frame(self.result_card_container, bg=bg, bd=0)
            card.pack(fill="x", pady=5, ipady=10)

            left_frame = tk.Frame(card, bg=bg)
            left_frame.pack(side="left", fill="x", expand=True, padx=(15, 5))
            icon = {"手机": "📱", "PC": "💻", "平板": "📟", "头像": "👤"}.get(scene, "")
            tk.Label(
                left_frame,
                text=f"{icon} {scene}",
                font=("Segoe UI", 13, "bold"),
                bg=bg,
                fg=self.colors["text"],
            ).pack(anchor="w")
            detail_text = f"最佳匹配比例: {info['best_match_ratio']} | 拉伸变形: {info['distortion_level']}"
            tk.Label(
                left_frame,
                text=detail_text,
                font=("Segoe UI", 9),
                bg=bg,
                fg=self.colors["text_light"],
            ).pack(anchor="w", pady=(2, 0))

            right_frame = tk.Frame(card, bg=bg)
            right_frame.pack(side="right", fill="y", padx=(5, 15))

            if info["suitable"]:
                status_text, status_color = "✓ 适配", self.colors["green"]
            else:
                if not info["ratio_suitable"]:
                    status_text, status_color = "✕ 比例不符", self.colors["red"]
                else:
                    status_text, status_color = "✓ 分辨率不足", self.colors["green"]
            tk.Label(
                right_frame,
                text=status_text,
                font=("Segoe UI", 11, "bold"),
                bg=bg,
                fg=status_color,
            ).pack(expand=True)

    def get_distortion_level(self, difference: float) -> str:
        if difference <= 0.02:
            return "几乎无"
        elif difference <= 0.05:
            return "轻微"
        elif difference <= 0.10:
            return "中等"
        elif difference <= 0.20:
            return "明显"
        else:
            return "严重"

    def update_image_preview(self, image_path: str):
        self.current_image_path = image_path
        self._redraw_canvas()

    def batch_analyze(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if not folder_path:
            return
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
        image_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.splitext(f.lower())[1] in image_extensions
        ]
        if not image_files:
            messagebox.showwarning("提示", "所选文件夹中没有找到图片！")
            return
        results_summary = []
        for image_path in image_files:
            try:
                analysis = self.analyze_image(image_path)
                filename = os.path.basename(image_path)
                best_scene_info = (
                    f"最适配: {analysis['best_scene']}"
                    if analysis["best_scene"] != "其他"
                    else "无完美适配场景"
                )
                results_summary.append(f"{filename}: {best_scene_info}")
            except Exception as e:
                filename = os.path.basename(image_path)
                results_summary.append(f"{filename}: 分析失败 - {str(e)}")
        self.show_batch_results(results_summary)

    def show_batch_results(self, results: List[str]):
        result_window = tk.Toplevel(self.root)
        result_window.title("批量分析结果")
        result_window.geometry("600x400")
        result_window.configure(bg="#f0f0f0")
        text_frame = tk.Frame(result_window, bg="#f0f0f0")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget = tk.Text(text_frame, font=("Segoe UI", 10), wrap="word", bd=0)
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for result in results:
            text_widget.insert(tk.END, result + "\n")
        text_widget.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


def main():
    try:
        app = ImageSceneAnalyzer()
        app.run()
    except Exception as e:
        messagebox.showerror("严重错误", f"应用程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
