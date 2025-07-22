import os
import sys
import subprocess
import platform


def build_windows():
    """构建Windows可执行文件"""
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 无控制台窗口
        "--name=智能图片场景分析器",  # 应用程序名称
        "--icon=app_icon.ico",  # 应用图标（如果有的话）
        "--add-data=README.md;.",  # 添加说明文件
        "--hidden-import=PIL._tkinter_finder",  # 隐式导入
        "image_scene_analyzer.py",  # 主程序文件
    ]

    print("正在构建Windows版本...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("✅ Windows版本构建成功！")
        print("可执行文件位置: dist/智能图片场景分析器.exe")
    else:
        print("❌ Windows版本构建失败！")


def build_mac():
    """构建Mac应用程序"""
    # 第一步：使用PyInstaller创建.app文件
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=智能图片场景分析器",
        "--icon=app_icon.icns",  # Mac图标格式
        "--add-data=README.md:.",
        "--hidden-import=PIL._tkinter_finder",
        "image_scene_analyzer.py",
    ]

    print("正在构建Mac应用程序...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("✅ Mac .app文件构建成功！")

        # 第二步：创建DMG文件
        create_dmg()
    else:
        print("❌ Mac应用程序构建失败！")


def create_dmg():
    """创建DMG安装包（仅限Mac系统）"""
    if platform.system() != "Darwin":
        print("⚠️  DMG文件只能在Mac系统上创建")
        return

    app_name = "智能图片场景分析器"

    # 创建临时文件夹
    os.makedirs("dmg_temp", exist_ok=True)

    # 复制.app文件到临时文件夹
    subprocess.run(["cp", "-R", f"dist/{app_name}.app", "dmg_temp/"])

    # 创建DMG文件
    dmg_cmd = [
        "hdiutil",
        "create",
        "-volname",
        app_name,
        "-srcfolder",
        "dmg_temp",
        "-ov",
        "-format",
        "UDZO",
        f"dist/{app_name}.dmg",
    ]

    result = subprocess.run(dmg_cmd)
    if result.returncode == 0:
        print(f"✅ DMG文件创建成功: dist/{app_name}.dmg")
    else:
        print("❌ DMG文件创建失败")

    # 清理临时文件
    subprocess.run(["rm", "-rf", "dmg_temp"])


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("python build_app.py windows  # 构建Windows版本")
        print("python build_app.py mac      # 构建Mac版本")
        print("python build_app.py all      # 构建所有版本")
        return

    target = sys.argv[1].lower()

    # 确保依赖已安装
    print("检查依赖...")
    try:
        import PIL

        print("✅ Pillow已安装")
    except ImportError:
        print("❌ 请先安装Pillow: pip install Pillow")
        return

    # 检查PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
        print("✅ PyInstaller已安装")
    except:
        print("❌ 请先安装PyInstaller: pip install pyinstaller")
        return

    if target == "windows":
        build_windows()
    elif target == "mac":
        build_mac()
    elif target == "all":
        if platform.system() == "Windows":
            build_windows()
        elif platform.system() == "Darwin":
            build_mac()
        else:
            print("❌ 不支持的操作系统")
    else:
        print("❌ 不支持的构建目标")


if __name__ == "__main__":
    main()
