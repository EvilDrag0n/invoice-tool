import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

from invoice_tool.gui.controller import Controller, AppPhase, map_process_result_to_gui_data

class InvoiceApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("发票提取工具")
        self.geometry("1080x840")
        self.minsize(900, 680)
        
        self.controller = Controller(self)
        
        self._setup_styles()
        self._build_layout()
        self._pane_init_retry = 0
        self.after(80, self._set_initial_pane_layout)

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')  # A clean, modern base theme
        
        # Colors
        self.bg_color = "#f3f6fb"
        self.card_bg = "#ffffff"
        self.text_primary = "#1f2937"
        self.text_secondary = "#6b7280"
        self.accent_color = "#2563eb"
        self.border_color = "#d6deeb"
        self.success_color = "#15803d"
        self.warn_color = "#b45309"
        self.error_color = "#b91c1c"

        self.configure(bg=self.bg_color)
        
        # General Styles
        style.configure(".", background=self.bg_color, foreground=self.text_primary, font=("Segoe UI", 10))
        
        # Header Style
        style.configure("Header.TLabel", font=("Segoe UI", 17, "bold"), padding=(0, 10, 0, 4))
        style.configure("HeaderSub.TLabel", font=("Segoe UI", 10), foreground="#64748b", background=self.bg_color)
        
        # Section Frames (Cards)
        style.configure("Card.TFrame", background=self.card_bg, relief="solid", borderwidth=1)
        style.configure("Group.TLabelframe", background=self.card_bg, relief="solid", borderwidth=1)
        style.configure("Group.TLabelframe.Label", background=self.bg_color, foreground=self.accent_color, font=("Segoe UI", 10, "bold"))
        
        # Labels within cards
        style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_primary)
        style.configure("CardSecondary.TLabel", background=self.card_bg, foreground=self.text_secondary, font=("Segoe UI", 9))
        style.configure("SectionTitle.TLabel", background=self.card_bg, font=("Segoe UI", 11, "bold"), foreground=self.accent_color)
        style.configure("MetricName.TLabel", background=self.card_bg, foreground=self.text_secondary, font=("Segoe UI", 10))
        style.configure("MetricValueNormal.TLabel", background=self.card_bg, foreground="#1f2937", font=("Segoe UI", 15, "bold"))
        style.configure("MetricValueAlert.TLabel", background=self.card_bg, foreground="#c62828", font=("Segoe UI", 15, "bold"))
        style.configure("StatusNeutral.TLabel", background=self.card_bg, foreground=self.text_secondary, font=("Segoe UI", 10, "bold"))
        style.configure("StatusRunning.TLabel", background=self.card_bg, foreground=self.accent_color, font=("Segoe UI", 10, "bold"))
        style.configure("StatusSuccess.TLabel", background=self.card_bg, foreground=self.success_color, font=("Segoe UI", 10, "bold"))
        style.configure("StatusWarn.TLabel", background=self.card_bg, foreground=self.warn_color, font=("Segoe UI", 10, "bold"))
        style.configure("StatusError.TLabel", background=self.card_bg, foreground=self.error_color, font=("Segoe UI", 10, "bold"))

        # Buttons
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.map("Action.TButton", 
                  background=[('active', '#1d4ed8'), ('!disabled', self.accent_color)],
                  foreground=[('!disabled', 'white')])
        style.configure("Soft.TButton", font=("Segoe UI", 9), padding=(10, 6), foreground=self.text_primary)

        style.configure("TNotebook", background=self.card_bg, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 6), font=("Segoe UI", 9, "bold"))
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.accent_color), ("active", "#dbeafe"), ("!selected", "#e5e7eb")],
            foreground=[("selected", "#ffffff"), ("active", "#1e3a8a"), ("!selected", "#334155")]
        )

        # Dedicated style for detail tabs to avoid selected-state shrink illusion.
        style.configure("Detail.TNotebook", background=self.card_bg, borderwidth=0)
        style.configure("Detail.TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10))
        style.map(
            "Detail.TNotebook.Tab",
            background=[("selected", self.accent_color), ("active", "#dbeafe"), ("!selected", "#e5e7eb")],
            foreground=[("selected", "#ffffff"), ("active", "#1e3a8a"), ("!selected", "#334155")],
            font=[("selected", ("Segoe UI", 10, "bold")), ("!selected", ("Segoe UI", 9))],
            padding=[("selected", (14, 9)), ("!selected", (12, 6))]
        )

    def _build_layout(self):
        # Main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header
        header = ttk.Label(main_frame, text="发票提取工具", style="Header.TLabel")
        header.pack(fill=tk.X)
        subtitle = ttk.Label(main_frame, text="支持拖放与批量处理，实时展示处理状态与异常明细", style="HeaderSub.TLabel")
        subtitle.pack(fill=tk.X, pady=(0, 14))

        # 2. Input Card
        self._build_input_card(main_frame)
        
        # 3. Output Card
        self._build_output_card(main_frame)

        # 4. Action / Progress Area
        self._build_action_area(main_frame)

        # 5. Summary & Details Area (PanedWindow for adjustability)
        self.main_paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self._build_summary_section(self.main_paned)
        self._build_details_section(self.main_paned)

    def _set_initial_pane_layout(self):
        if not hasattr(self, "main_paned"):
            return
        self.update_idletasks()
        if len(self.main_paned.panes()) < 2:
            return
        total_h = self.main_paned.winfo_height()
        if total_h < 260:
            self._pane_init_retry += 1
            if self._pane_init_retry <= 8:
                self.after(80, self._set_initial_pane_layout)
            return
        # Keep summary area comfortably visible at startup.
        summary_h = max(130, min(int(total_h * 0.40), total_h - 260))
        try:
            self.main_paned.sashpos(0, summary_h)
        except Exception:
            pass

    def _build_input_card(self, parent):
        self.input_card = ttk.LabelFrame(parent, text=" 输入来源 ", style="Group.TLabelframe")
        self.input_card.pack(fill=tk.X, pady=(0, 10))
        
        # Inner padding frame (ttk Frames don't support inner padding directly well)
        self.input_inner = ttk.Frame(self.input_card, style="Card.TFrame", padding=15)
        self.input_inner.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.btn_frame = ttk.Frame(self.input_inner, style="Card.TFrame")
        self.btn_frame.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.btn_choose_file = ttk.Button(self.btn_frame, text="选择文件...", style="Soft.TButton", command=self._on_choose_file)
        self.btn_choose_file.pack(side=tk.LEFT, padx=(0, 5))
        self.btn_choose_folder = ttk.Button(self.btn_frame, text="选择文件夹...", style="Soft.TButton", command=self._on_choose_folder)
        self.btn_choose_folder.pack(side=tk.LEFT)

        # Selected path display
        ttk.Label(self.input_inner, text="已选路径：", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        
        self.input_path_var = tk.StringVar(value="未选择")
        path_label = ttk.Label(self.input_inner, textvariable=self.input_path_var, style="CardSecondary.TLabel", wraplength=500)
        path_label.grid(row=1, column=1, sticky="w", padx=10)
        
        # Mode display
        self.input_mode_var = tk.StringVar(value="（可拖放 PDF 文件或文件夹到此处）")
        ttk.Label(self.input_inner, textvariable=self.input_mode_var, style="CardSecondary.TLabel").grid(row=1, column=2, sticky="e")
        
        self.input_inner.columnconfigure(1, weight=1)

        # Register Drop Target
        self.input_card.drop_target_register(DND_FILES)
        self.input_card.dnd_bind('<<Drop>>', self._on_drop)
        self.input_inner.drop_target_register(DND_FILES)
        self.input_inner.dnd_bind('<<Drop>>', self._on_drop)

    def _on_choose_file(self):
        if self.controller.state.phase == AppPhase.PROCESSING:
            return
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self._update_input_from_path(path)

    def _on_choose_folder(self):
        if self.controller.state.phase == AppPhase.PROCESSING:
            return
        path = filedialog.askdirectory()
        if path:
            self._update_input_from_path(path)

    def _on_drop(self, event):
        if self.controller.state.phase == AppPhase.PROCESSING:
            return
        # tkinterdnd2 can return multiple files as a brace-delimited string
        # if they contain spaces. On Windows, backslashes might be doubled or escaped.
        # We use a regex to correctly split the tcl list string.
        data = event.data
        
        # Tcl list splitting: matches items inside {braces} or items without spaces
        files = re.findall(r'\{(.*?)\}|([^\s{}]+)', data)
        # findall with multiple groups returns a list of tuples, flatten and filter empty
        files = [item[0] if item[0] else item[1] for item in files]
        
        if len(files) > 1:
            self._set_status("错误：一次仅支持拖放 1 个文件或文件夹。", "error")
            return

        path = files[0]
        self._update_input_from_path(path)

    def _update_input_from_path(self, path):
        success, message = self.controller.set_input(path)
        if success:
            self.input_path_var.set(self.controller.state.input_path)
            mode_text = "文件" if self.controller.state.input_mode.value == "file" else "文件夹"
            self.input_mode_var.set(f"模式：{mode_text}")
            self._set_status(message)
        else:
            self._set_status(f"错误：{message}", "error")
            messagebox.showerror("输入无效", message)

    def _build_output_card(self, parent):
        self.output_card = ttk.LabelFrame(parent, text=" 输出位置 ", style="Group.TLabelframe")
        self.output_card.pack(fill=tk.X, pady=(0, 15))
        
        self.output_inner = ttk.Frame(self.output_card, style="Card.TFrame", padding=15)
        self.output_inner.pack(fill=tk.BOTH, expand=True)

        self.btn_choose_output = ttk.Button(self.output_inner, text="选择输出...", style="Soft.TButton", command=self._on_choose_output)
        self.btn_choose_output.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.output_path_var = tk.StringVar(value="未选择")
        out_label = ttk.Label(self.output_inner, textvariable=self.output_path_var, style="CardSecondary.TLabel", wraplength=600)
        out_label.grid(row=0, column=1, sticky="w", padx=10)

        self.overwrite_var = tk.BooleanVar(value=False)
        self.check_overwrite = ttk.Checkbutton(self.output_inner, text="允许覆盖已有文件", variable=self.overwrite_var, style="Card.TCheckbutton")
        self.check_overwrite.grid(row=1, column=0, columnspan=2, sticky="w")
        
        self.output_inner.columnconfigure(1, weight=1)

    def _on_choose_output(self):
        if self.controller.state.phase == AppPhase.PROCESSING:
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.controller.set_output(path)
            self.output_path_var.set(path)
            self._set_status("输出路径已更新。")

    def _build_action_area(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill=tk.X, pady=(0, 10))
        frame = ttk.Frame(card, style="Card.TFrame", padding=14)
        frame.pack(fill=tk.X)

        # Start Button
        self.start_btn_default_text = "开始处理"
        self.start_btn_running_text = "处理中..."
        self.start_btn = ttk.Button(frame, text=self.start_btn_default_text, style="Action.TButton", command=self._on_start)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 16))

        # Progress elements
        progress_frame = ttk.Frame(frame, style="Card.TFrame")
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, style="StatusNeutral.TLabel")
        self.status_label.pack(anchor="w", pady=(0, 4))

        phase_row = ttk.Frame(progress_frame, style="Card.TFrame")
        phase_row.pack(fill=tk.X, pady=(0, 4))
        self.phase_var = tk.StringVar(value="当前阶段：待命")
        self.percent_var = tk.StringVar(value="0%")
        ttk.Label(phase_row, textvariable=self.phase_var, style="CardSecondary.TLabel").pack(side=tk.LEFT)
        ttk.Label(phase_row, textvariable=self.percent_var, style="CardSecondary.TLabel").pack(side=tk.RIGHT)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X)

    def _on_start(self):
        # 1. Basic validation
        if not self.controller.state.input_path:
            messagebox.showwarning("缺少输入", "请选择 PDF 文件或文件夹。")
            return
        if not self.controller.state.output_path:
            messagebox.showwarning("缺少输出", "请选择输出 Excel 文件。")
            return

        # 2. Sync state
        self.controller.state.overwrite = self.overwrite_var.get()

        # 3. UI transitions
        self._set_ui_state(AppPhase.PROCESSING)
        self._set_status("正在启动...", "validating")
        self._set_phase_percent("validating", "0%")
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start(10)
        self.progress_var.set(0)
        
        # Clear details
        self.fail_text.config(state=tk.NORMAL)
        self.fail_text.delete("1.0", tk.END)
        self.fail_text.config(state=tk.DISABLED)
        self.conflict_text.config(state=tk.NORMAL)
        self.conflict_text.delete("1.0", tk.END)
        self.conflict_text.config(state=tk.DISABLED)
        self._update_detail_tab_badges(0, 0)

        # 4. Trigger
        self.controller.start_processing()
        self.after(100, self._poll_queue)

    def _set_ui_state(self, phase: AppPhase):
        self.controller.state.phase = phase
        if phase == AppPhase.PROCESSING:
            self.start_btn.config(state=tk.DISABLED)
            self.start_btn.config(text=self.start_btn_running_text)
            self.btn_choose_file.config(state=tk.DISABLED)
            self.btn_choose_folder.config(state=tk.DISABLED)
            self.btn_choose_output.config(state=tk.DISABLED)
            self.check_overwrite.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.start_btn.config(text=self.start_btn_default_text)
            self.btn_choose_file.config(state=tk.NORMAL)
            self.btn_choose_folder.config(state=tk.NORMAL)
            self.btn_choose_output.config(state=tk.NORMAL)
            self.check_overwrite.config(state=tk.NORMAL)

    def _poll_queue(self):
        try:
            while True:
                msg_type, data = self.controller.event_queue.get_nowait()
                if msg_type == "progress":
                    self._handle_progress(data)
                elif msg_type == "result":
                    self._handle_result(data)
                    return # Stop polling
                elif msg_type == "error":
                    self._handle_error(data)
                    return # Stop polling
        except tk.TclError:
            # Handle case where widget is destroyed during poll
            return
        except Exception:
            # No message in queue
            pass
        
        # Continue polling if not done
        if self.controller.state.phase == AppPhase.PROCESSING:
            self.after(100, self._poll_queue)

    def _handle_progress(self, event):
        self._set_status(_localize_phase_message(event.phase, event.message), event.phase)
        
        # Phase-based progress semantics: indeterminate for preflight/setup, determinate for processing
        if event.phase in ("validating", "exporting"):
            if self.progress_bar['mode'] != 'indeterminate':
                self.progress_bar.configure(mode='indeterminate')
                self.progress_bar.start(10)
        else:
            if self.progress_bar['mode'] != 'determinate':
                self.progress_bar.stop()
                self.progress_bar.configure(mode='determinate')
            
            if event.phase == "complete":
                self.progress_var.set(100)
                self._set_phase_percent(event.phase, "100%")
            elif event.total > 0:
                pct = (event.completed / event.total) * 100
                self.progress_var.set(pct)
                self._set_phase_percent(event.phase, f"{pct:.0f}%")
            else:
                self.progress_var.set(0)
                self._set_phase_percent(event.phase, "0%")
        if event.phase in ("validating", "exporting"):
            self._set_phase_percent(event.phase, "--")

    def _handle_result(self, result):
        summary, details = map_process_result_to_gui_data(result)
        
        # Update metrics
        for key, var in self.metric_vars.items():
            var.set(str(getattr(summary, key)))
        self._refresh_summary_alerts(summary)
            
        # Update details
        self.fail_text.config(state=tk.NORMAL)
        self.fail_text.insert(tk.END, "\n".join(details.failed_files))
        self.fail_text.config(state=tk.DISABLED)
        
        self.conflict_text.config(state=tk.NORMAL)
        self.conflict_text.insert(tk.END, "\n".join(details.conflict_lines))
        self.conflict_text.config(state=tk.DISABLED)
        self._update_detail_tab_badges(len(details.failed_files), len(details.conflict_lines))
        
        self._set_status("处理完成。", "complete")
        self._set_phase_percent("complete", "100%")
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.progress_var.set(100)
        self._set_ui_state(AppPhase.SUCCESS)
        messagebox.showinfo("完成", f"成功导出 {summary.exported} 条记录：\n{result.output_path}")

    def _handle_error(self, event):
        # Stop any active animation and ensure determinate mode on error
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        
        # Support both raw strings and ProgressEvent objects for robustness
        message = event.message if hasattr(event, 'message') else str(event)
        
        self._set_status(f"错误：{message}", "error")
        self._set_phase_percent("error", "--")
        self._update_detail_tab_badges(0, 0)
        self._set_ui_state(AppPhase.FAILURE)
        messagebox.showerror("处理失败", message)

    def _set_phase_percent(self, phase: str, percent_text: str):
        phase_map = {
            "validating": "校验输入",
            "processing": "处理中",
            "exporting": "导出中",
            "complete": "已完成",
            "error": "处理失败",
            "": "待命",
        }
        self.phase_var.set(f"当前阶段：{phase_map.get(phase, phase)}")
        self.percent_var.set(f"进度：{percent_text}")

    def _set_status(self, text: str, phase: str = ""):
        self.status_var.set(text)
        if not hasattr(self, "status_label"):
            return
        if phase in ("processing", "validating", "exporting"):
            self.status_label.configure(style="StatusRunning.TLabel")
        elif phase == "complete":
            self.status_label.configure(style="StatusSuccess.TLabel")
        elif phase == "error":
            self.status_label.configure(style="StatusError.TLabel")
        elif "错误" in text:
            self.status_label.configure(style="StatusError.TLabel")
        elif "已更新" in text:
            self.status_label.configure(style="StatusWarn.TLabel")
        else:
            self.status_label.configure(style="StatusNeutral.TLabel")

    def _build_summary_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        parent.add(card, weight=1)
        
        inner = ttk.Frame(card, style="Card.TFrame", padding=15)
        inner.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(inner, text="处理汇总", style="SectionTitle.TLabel")
        title.pack(anchor="w", pady=(0, 10))

        metrics_frame = ttk.Frame(inner, style="Card.TFrame")
        metrics_frame.pack(fill=tk.X)

        self.metric_vars = {}
        self.metric_value_labels = {}
        metrics = [
            ("📄", "已处理", "processed", "#eaf2ff", "#1e40af", "#1e40af"),
            ("✅", "已导出", "exported", "#e8f8ef", "#166534", "#166534"),
            ("🟨", "部分提取", "incomplete_exported", "#fff8e1", "#a16207", "#ca8a04"),
            ("⚠", "失败", "skipped_failed", "#fff1f2", "#9f1239", "#dc2626"),
            ("↺", "重复跳过", "skipped_duplicate", "#fff7e6", "#92400e", "#92400e"),
            ("‼", "冲突", "duplicate_conflicts", "#fff4e5", "#9a3412", "#ea580c")
        ]

        for i, (icon, label_text, key, bg, normal_fg, alert_fg) in enumerate(metrics):
            m_frame = tk.Frame(
                metrics_frame,
                bg=bg,
                bd=1,
                relief="solid",
                padx=12,
                pady=10,
                highlightthickness=1,
                highlightbackground="#ffffff",
                highlightcolor="#ffffff",
            )
            m_frame.grid(row=0, column=i, padx=(0, 16) if i < len(metrics)-1 else 0, sticky="nsew")

            row = tk.Frame(m_frame, bg=bg)
            row.pack(fill=tk.X, expand=True)

            left = tk.Frame(row, bg=bg)
            left.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(left, text=f"{icon} {label_text}", bg=bg, fg=self.text_secondary, font=("Segoe UI", 9, "bold")).pack(anchor="w")

            var = tk.StringVar(value="0")
            self.metric_vars[key] = var
            value_label = tk.Label(row, textvariable=var, bg=bg, fg=normal_fg, font=("Segoe UI", 17, "bold"))
            value_label.pack(side=tk.RIGHT, anchor="e")
            self.metric_value_labels[key] = (value_label, normal_fg, alert_fg)

        for i in range(len(metrics)):
            metrics_frame.columnconfigure(i, weight=1)

        self._refresh_summary_alerts(None)

    def _refresh_summary_alerts(self, summary):
        if not hasattr(self, "metric_value_labels"):
            return
        for key, label_pack in self.metric_value_labels.items():
            label, normal_fg, alert_fg = label_pack
            try:
                value = int(self.metric_vars[key].get())
            except Exception:
                value = 0
            is_alert = key in ("skipped_failed", "duplicate_conflicts", "incomplete_exported") and value > 0
            label.configure(fg=alert_fg if is_alert else normal_fg)

    def _format_issue_tab_label(self, kind: str, count: int) -> str:
        if kind == "failed":
            return f"失败文件 ({count})"
        return f"冲突明细 ({count})"

    def _update_detail_tab_badges(self, failed_count: int, conflict_count: int):
        if not hasattr(self, "notebook"):
            return
        self.notebook.tab(0, text=self._format_issue_tab_label("failed", failed_count))
        self.notebook.tab(1, text=self._format_issue_tab_label("conflict", conflict_count))

    def _build_details_section(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        parent.add(card, weight=4)
        
        inner = ttk.Frame(card, style="Card.TFrame", padding=15)
        inner.pack(fill=tk.BOTH, expand=True)

        # Notebook for Failed Files / Conflicts
        self.notebook = ttk.Notebook(inner, style="Detail.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Failed Files Tab
        fail_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(fail_frame, text=self._format_issue_tab_label("failed", 0))
        
        self.fail_text = tk.Text(fail_frame, height=20, width=150, wrap=tk.NONE, font=("Consolas", 10), 
                                 bg="#ffffff", fg="#d32f2f", relief="solid", borderwidth=1, state=tk.DISABLED)
        fail_scroll_y = ttk.Scrollbar(fail_frame, orient=tk.VERTICAL, command=self.fail_text.yview)
        fail_scroll_x = ttk.Scrollbar(fail_frame, orient=tk.HORIZONTAL, command=self.fail_text.xview)
        self.fail_text.configure(yscrollcommand=fail_scroll_y.set, xscrollcommand=fail_scroll_x.set)
        
        fail_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        fail_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.fail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Conflicts Tab
        conflict_frame = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(conflict_frame, text=self._format_issue_tab_label("conflict", 0))
        
        self.conflict_text = tk.Text(conflict_frame, height=20, width=150, wrap=tk.NONE, font=("Consolas", 10),
                                     bg="#ffffff", fg="#f57c00", relief="solid", borderwidth=1, state=tk.DISABLED)
        conflict_scroll_y = ttk.Scrollbar(conflict_frame, orient=tk.VERTICAL, command=self.conflict_text.yview)
        conflict_scroll_x = ttk.Scrollbar(conflict_frame, orient=tk.HORIZONTAL, command=self.conflict_text.xview)
        self.conflict_text.configure(yscrollcommand=conflict_scroll_y.set, xscrollcommand=conflict_scroll_x.set)
        
        conflict_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        conflict_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.conflict_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


def main():
    app = InvoiceApp()
    app.mainloop()
    return 0


def _extract_filename_from_message(message: str) -> str:
    if not message:
        return ""
    m = re.search(r"Processing\s+(.*?)\.\.\.", message)
    if m:
        return m.group(1)
    return ""


def _localize_phase_message(phase: str, raw_message: str) -> str:
    if phase == "validating":
        return "正在校验输入..."
    if phase == "processing":
        file_name = _extract_filename_from_message(raw_message)
        return f"正在处理：{file_name}" if file_name else "正在处理发票..."
    if phase == "exporting":
        return "正在导出 Excel..."
    if phase == "complete":
        return "处理完成。"
    if phase == "error":
        return f"错误：{raw_message}" if raw_message else "处理失败。"
    return raw_message


if __name__ == "__main__":
    main()
