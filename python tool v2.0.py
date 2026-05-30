# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import ast
import sys

# 获取当前 Python 的标准库集合，用于过滤（兼容 Python 3.8 及以上）
try:
    # Python 3.10+ 内置了获取标准库名称的属性
    STD_LIBS = set(sys.stdlib_module_names)
except AttributeError:
    # Python 3.8 兼容硬编码列表 + sys.builtin_module_names
    STD_LIBS = set(sys.builtin_module_names).union({
        'os', 'sys', 'time', 'datetime', 'math', 'random', 'json', 're', 'csv', 'threading', 
        'subprocess', 'tkinter', 'urllib', 'pathlib', 'sqlite3', 'logging', 'argparse', 
        'itertools', 'collections', 'functools', 'socket', 'ast', 'shutil', 'hashlib',
        'typing', 'base64', 'uuid', 'copy', 'traceback'
    })

class UVToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 脚本运行与打包工具 V2.0")
        self.root.geometry("750x550")
        
        # --- 变量区 ---
        self.file_path_var = tk.StringVar()
        self.deps_var = tk.StringVar()  # 新增：用于存储动态识别的依赖包
        
        # --- 界面布局 ---
        # 1. 顶部选择文件区域
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, padx=15, fill=tk.X)
        
        tk.Label(top_frame, text="Python 脚本路径:", font=("Microsoft YaHei", 10), width=15, anchor='e').pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.file_path_var, state='readonly', width=55).pack(side=tk.LEFT, padx=10)
        tk.Button(top_frame, text="浏览...", command=self.browse_file).pack(side=tk.LEFT)

        # 2. 新增：依赖包动态调整区域
        deps_frame = tk.Frame(root)
        deps_frame.pack(pady=5, padx=15, fill=tk.X)
        
        tk.Label(deps_frame, text="所需依赖包:", font=("Microsoft YaHei", 10), width=15, anchor='e').pack(side=tk.LEFT)
        tk.Entry(deps_frame, textvariable=self.deps_var, width=55).pack(side=tk.LEFT, padx=10)
        tk.Label(deps_frame, text="(空格分隔，选文件会自动识别)", fg="gray", font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        
        # 3. 中部按钮区域
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.run_btn = tk.Button(btn_frame, text="? 运行脚本 (Run)", bg="#4CAF50", fg="white", 
                                 font=("Microsoft YaHei", 10, "bold"), width=20, command=self.run_script)
        self.run_btn.pack(side=tk.LEFT, padx=20)
        
        self.pack_btn = tk.Button(btn_frame, text="? 打包为 EXE", bg="#2196F3", fg="white", 
                                  font=("Microsoft YaHei", 10, "bold"), width=20, command=self.pack_exe)
        self.pack_btn.pack(side=tk.LEFT, padx=20)
        
        # 4. 底部日志输出区域
        tk.Label(root, text="运行日志 (Console Output):", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, padx=15)
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=18, bg="#1E1E1E", fg="#D4D4D4", font=("Consolas", 10))
        self.log_area.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

    def analyze_imports(self, file_path):
        """核心增强：自动分析目标脚本的 import 语句，提取第三方依赖"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)

            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            # 过滤标准库和内部隐藏模块
            third_party = [pkg for pkg in imports if pkg not in STD_LIBS and not pkg.startswith('_')]
            
            # 常见 [代码导入名] 与 [pip安装包名] 不一致的映射字典
            mapping = {
                'cv2': 'opencv-python',
                'PIL': 'Pillow',
                'bs4': 'beautifulsoup4',
                'sklearn': 'scikit-learn',
                'yaml': 'pyyaml'
            }
            resolved_deps = [mapping.get(pkg, pkg) for pkg in third_party]

            # 填入界面
            self.deps_var.set(" ".join(resolved_deps))
            if resolved_deps:
                self.log(f"[*] 自动识别到第三方库: {', '.join(resolved_deps)}")
            else:
                self.log("[*] 未检测到需要额外下载的第三方库，或全为标准库。")
                
        except Exception as e:
            self.log(f"[警告] 自动分析依赖库失败，可手动在上方文本框输入所需库名。\n({str(e)})")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择要运行或打包的 Python 脚本",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log_area.delete(1.0, tk.END) # 清空日志
            self.log(f"已选择脚本: {file_path}")
            # 触发自动依赖分析
            self.analyze_imports(file_path)

    def log(self, message):
        """将信息安全地插入到文本框中，并自动滚动到最底部"""
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def execute_command_thread(self, cmd_list, action_name):
        """在后台线程中执行命令"""
        self.log(f"\n========== 开始 {action_name} ==========")
        self.log(f"执行命令: {' '.join(cmd_list)}\n")
        
        self.run_btn.config(state=tk.DISABLED)
        self.pack_btn.config(state=tk.DISABLED)
        
        try:
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            for line in process.stdout:
                self.root.after(0, self.log, line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.root.after(0, self.log, f"\n========== {action_name} 成功完成! ==========\n")
            else:
                self.root.after(0, self.log, f"\n========== {action_name} 异常退出 (代码: {process.returncode}) ==========\n")
                
        except Exception as e:
            self.root.after(0, self.log, f"\n[系统错误]: 执行命令时发生异常:\n{str(e)}\n")
            
        finally:
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.pack_btn.config(state=tk.NORMAL))

    def get_uv_with_args(self):
        """动态生成 uv 的 --with 参数列表"""
        deps_str = self.deps_var.get().strip()
        if not deps_str:
            return []
        
        args = []
        for dep in deps_str.split():
            args.extend(["--with", dep])
        return args

    def run_script(self):
        script_path = self.file_path_var.get()
        if not script_path:
            messagebox.showwarning("提示", "请先选择一个 Python 脚本！")
            return
            
        # 动态组装命令
        cmd = ["uv", "run", "--python", "3.8.20"] + self.get_uv_with_args() + [script_path]
        
        threading.Thread(target=self.execute_command_thread, args=(cmd, "运行脚本"), daemon=True).start()

    def pack_exe(self):
        script_path = self.file_path_var.get()
        if not script_path:
            messagebox.showwarning("提示", "请先选择一个 Python 脚本！")
            return
            
        # 打包需要带上 pyinstaller，以及脚本本身的依赖
        cmd = ["uv", "run", "--python", "3.8.20", "--with", "pyinstaller"] + \
              self.get_uv_with_args() + \
              ["pyinstaller", "--onefile", "--noconsole", script_path]
        
        threading.Thread(target=self.execute_command_thread, args=(cmd, "打包 EXE"), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.update_idletasks()
    width = 750
    height = 550
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    app = UVToolApp(root)
    root.mainloop()