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
        self.root.configure(bg="#f0f0f0")

        # 场景标准比例定义（宽:高）
        self.scene_ratios = {
            "头像": [(1, 1)],  # 正方形
            "手机": [(9, 16), (9, 18), (9, 19.5), (10, 16), (2, 3)],  # 手机比例
            "平板": [(4, 3), (16, 10), (3, 2), (5, 4)],  # 平板比例
            "PC": [(16, 9), (21, 9), (16, 10), (4, 3), (5, 4), (3, 2)],  # PC比例
        }

        # 容差范围
        self.tolerance = 0.05

        # self.current_image_path = None
        # self.current_image = None
        self.analysis_results = {}

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # # 主标题
        # title_label = tk.Label(
        #     self.root,
        #     text="图片场景分析器",
        #     font=("Arial", 16, "bold"),
        #     bg="#f0f0f0",
        #     fg="#333333",
        # )
        # title_label.pack(pady=10)

        # 上传按钮区域
        upload_frame = tk.Frame(self.root, bg="#f0f0f0")
        upload_frame.pack(pady=10)

        upload_btn = tk.Button(
            upload_frame,
            text="选择文件",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            command=self.select_image,
        )
        upload_btn.pack(side=tk.LEFT, padx=5)

        batch_btn = tk.Button(
            upload_frame,
            text="批量分析",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10,
            command=self.batch_analyze,
        )
        batch_btn.pack(side=tk.LEFT, padx=5)

        # 图片预览区域
        self.preview_frame = tk.LabelFrame(
            self.root,
            text="图片预览",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        self.preview_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.image_label = tk.Label(
            self.preview_frame,
            text="请选择文件",
            font=("Arial", 12),
            bg="white",
            fg="#666666",
            width=60,
            height=10,
        )
        self.image_label.pack(pady=10, padx=10, fill="both", expand=True)

        # 分析结果区域
        self.results_frame = tk.LabelFrame(
            self.root,
            text="分析结果",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="#333333",
        )
        self.results_frame.pack(pady=10, padx=20, fill="x")

        # 创建结果显示区域
        self.results_text = tk.Text(
            self.results_frame,
            height=8,
            font=("Arial", 10),
            bg="white",
            fg="#333333",
            wrap=tk.WORD,
        )
        self.results_text.pack(pady=10, padx=10, fill="x")

    def select_image(self):
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
            # ("所有文件", "*.*"),
        ]

        file_path = filedialog.askopenfilename(
            title="选择文件", filetypes=file_types
        )

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

            # self.current_image_path = image_path

        except Exception as e:
            messagebox.showerror("错误", f"处理时发生错误: {str(e)}")

    def analyze_image(self, image_path: str) -> Dict:
        """分析图片场景适用性"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            raise Exception(f"无法打开文件: {str(e)}")

        # 计算图片比例
        image_ratio = width / height

        # 分析各个场景的适用性
        scene_analysis = {}
        suitable_scenes = []

        for scene_name, ratios in self.scene_ratios.items(): # 枚举所有标准比例
            is_suitable = False
            best_match_ratio = None
            min_difference = float("inf")

            for standard_w, standard_h in ratios:
                standard_ratio = standard_w / standard_h
                # 差异度：实际比例 - 标准比例 / 标准比例
                difference = abs(image_ratio - standard_ratio) / standard_ratio

                if difference < min_difference:
                    min_difference = difference
                    best_match_ratio = f"{standard_w}:{standard_h}"

                # 检查是否在容差范围内
                if difference <= self.tolerance:
                    is_suitable = True

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
        """更新图片预览"""
        try:
            # 打开并调整图片大小用于预览
            with Image.open(image_path) as img:
                # 计算预览尺寸（保持比例）
                preview_width = 400
                preview_height = 200

                img_ratio = img.width / img.height
                if img_ratio > preview_width / preview_height:
                    new_width = preview_width
                    new_height = int(preview_width / img_ratio)
                else:
                    new_height = preview_height
                    new_width = int(preview_height * img_ratio)

                img_resized = img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )
                photo = ImageTk.PhotoImage(img_resized)

                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo  # 保持引用

        except Exception as e:
            self.image_label.configure(image="", text=f"预览失败: {str(e)}", fg="red")

    def display_results(self):
        """显示分析结果"""
        if not self.analysis_results:
            return

        results = self.analysis_results

        # 清空之前的结果
        self.results_text.delete(1.0, tk.END)

        # 基本信息
        basic_info = f"""基本信息
分辨率: {results['width']} × {results['height']}
宽高比例: {results['ratio']:.3f}:1
推荐场景: {results['best_scene']}

"""
        self.results_text.insert(tk.END, basic_info)

        # 各场景适用性分析
        self.results_text.insert(tk.END, " 各场景适用性分析\n")
        self.results_text.insert(tk.END, "-" * 40 + "\n")

        for scene_name, analysis in results["scene_analysis"].items():
            status = " 适用" if analysis["suitable"] else " 不适用"

            scene_detail = f"""
{scene_name}: {status}
  最佳匹配比例: {analysis['best_match_ratio']}
  变形程度: {analysis['distortion_level']}
  差异度: {analysis['difference']*100:.2f}%
"""
            self.results_text.insert(tk.END, scene_detail)

        # 使用建议
        if results["best_scene"] == "其他":
            suggestion = """
 使用建议
此图片在标准场景下使用可能会出现明显的拉伸或压缩变形。
建议用于特殊用途或进行裁剪后再使用。
"""
        else:
            suitable_count = len(results["suitable_scenes"])
            if suitable_count == 1:
                suggestion = f"""
 使用建议
此图片最适合用于{results['best_scene']}场景，显示效果最佳。
"""
            else:
                other_scenes = [
                    s for s in results["suitable_scenes"] if s != results["best_scene"]
                ]
                suggestion = f"""
 使用建议
此图片最适合用于{results['best_scene']}场景。
也可用于: {', '.join(other_scenes)}
"""

        self.results_text.insert(tk.END, suggestion)

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
