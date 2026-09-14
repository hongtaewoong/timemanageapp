import time
import customtkinter as ctk

# 기본 테마 및 색상 설정 (System, Dark, Light 중 선택 가능)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TodoApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    # 1. 창 기본 설정
    self.title("나의 할 일 목록 (To-Do List)")
    self.geometry("430x900")
    self.resizable(False, False)

    # 2. 메인 타이틀 라벨
    self.title_label = ctk.CTkLabel(
        self, text="Task Manager", font=ctk.CTkFont(size=24, weight="bold")
    )
    self.title_label.pack(pady=(20, 10))

    # 3. 입력 프레임 (텍스트 입력창 + 추가 버튼)
    self.input_frame = ctk.CTkFrame(self)
    self.input_frame.pack(fill="x", padx=20, pady=10)

    self.entry = ctk.CTkEntry(
        self.input_frame, placeholder_text="할 일을 입력하세요...", width=250
    )
    self.entry.pack(side="left", padx=(10, 5), pady=10)
    self.entry.bind("<Return>", lambda event: self.add_task())

    self.add_button = ctk.CTkButton(
        self.input_frame, text="추가", width=70, command=self.add_task
    )
    self.add_button.pack(side="right", padx=(5, 10), pady=10)

    # 4. 현재 진행 중인 일정 패널
    self.current_task_label = ctk.CTkLabel(
        self, text="현재 진행 중인 일정", font=ctk.CTkFont(size=18, weight="bold")
    )
    self.current_task_label.pack(anchor="w", padx=20, pady=(10, 5))

    self.current_task_frame = ctk.CTkFrame(self, corner_radius=12)
    self.current_task_frame.pack(fill="x", padx=20, pady=(0, 10))

    self.current_task_name = ctk.CTkLabel(
        self.current_task_frame,
        text="없음",
        font=ctk.CTkFont(size=20, weight="bold"),
        anchor="w",
    )
    self.current_task_name.pack(anchor="w", padx=20, pady=(20, 5), fill="x")

    self.current_task_timer = ctk.CTkLabel(
        self.current_task_frame,
        text="00:00:00",
        font=ctk.CTkFont(size=32, weight="bold"),
        text_color="#2E7D32",
    )
    self.current_task_timer.pack(anchor="center", pady=(5, 20))

    # 5. 할 일 목록 섹션
    self.active_title = ctk.CTkLabel(
        self, text="할 일 목록", font=ctk.CTkFont(size=16, weight="bold")
    )
    self.active_title.pack(anchor="w", padx=20, pady=(10, 5))

    self.active_frame = ctk.CTkScrollableFrame(self, width=340, height=60)
    self.active_frame.pack(padx=20, pady=(0, 10), fill="x")

    # 6. 완료한 일정 섹션
    self.completed_title = ctk.CTkLabel(
        self, text="완료한 일정", font=ctk.CTkFont(size=16, weight="bold")
    )
    self.completed_title.pack(anchor="w", padx=20, pady=(10, 5))

    self.completed_frame = ctk.CTkScrollableFrame(self, width=340, height=200)
    self.completed_frame.pack(padx=20, pady=(0, 20), fill="x")

    self.current_task = None
    self.current_task_started_at = None
    self.timer_job = None

  def add_task(self):
    task_text = self.entry.get().strip()
    if not task_text:
      return

    self.create_task_row(task_text, self.active_frame)
    self.entry.delete(0, "end")

  def create_task_row(self, task_text, parent, is_completed=False, elapsed_seconds=0):
    task_row = ctk.CTkFrame(parent)
    task_row.pack(fill="x", pady=5, padx=5)
    task_row.task_text = task_text
    task_row.start_time = None
    task_row.elapsed_seconds = elapsed_seconds

    task_label = ctk.CTkLabel(
        task_row, text=task_text, font=("맑은 고딕", 13), anchor="w"
    )
    task_label.pack(side="left", padx=10, pady=8, expand=True, fill="x")

    if is_completed:
      task_row.configure(fg_color="#E8F5E9")
      duration_label = ctk.CTkLabel(
          task_row,
          text=f"소요시간: {self.format_duration(elapsed_seconds)}",
          font=("맑은 고딕", 11, "bold"),
          text_color="#2E7D32",
      )
      duration_label.pack(side="right", padx=(0, 10), pady=8)

      delete_button = ctk.CTkButton(
          task_row,
          text="삭제",
          width=50,
          fg_color="#E53935",
          hover_color="#B71C1C",
          command=lambda: self.delete_task(task_row),
      )
      delete_button.pack(side="right", padx=(0, 10), pady=8)
      return

    start_button = ctk.CTkButton(
        task_row,
        text="시작",
        width=55,
        command=lambda: self.start_task(task_row),
    )
    start_button.pack(side="right", padx=(0, 5), pady=8)

    complete_button = ctk.CTkButton(
        task_row,
        text="완료",
        width=55,
        fg_color="#2E7D32",
        hover_color="#1B5E20",
        command=lambda: self.complete_task(task_row),
    )
    complete_button.pack(side="right", padx=(0, 5), pady=8)

    delete_button = ctk.CTkButton(
        task_row,
        text="삭제",
        width=50,
        fg_color="#E53935",
        hover_color="#B71C1C",
        command=lambda: self.delete_task(task_row),
    )
    delete_button.pack(side="right", padx=(0, 10), pady=8)

    task_row.start_button = start_button
    task_row.complete_button = complete_button

  def start_task(self, task_row):
    if self.current_task is not None and self.current_task is not task_row:
      self.stop_current_task()

    if task_row.start_time is None:
      task_row.start_time = time.perf_counter()
      self.current_task = task_row
      self.current_task_started_at = task_row.start_time
      task_row.start_button.configure(text="진행중")
      task_row.start_button.configure(fg_color="#FF9800", hover_color="#F57C00")
      self.update_current_task_display()
      self.start_timer()

  def stop_current_task(self):
    if self.current_task is None:
      return

    if self.current_task.start_time is not None:
      self.current_task.start_time = None
      self.current_task.start_button.configure(text="시작")
      self.current_task.start_button.configure(fg_color="#3B8ED0", hover_color="#2B6CB0")

    self.current_task = None
    self.current_task_started_at = None
    self.current_task_name.configure(text="없음")
    self.current_task_timer.configure(text="00:00:00")
    if self.timer_job is not None:
      self.after_cancel(self.timer_job)
      self.timer_job = None

  def complete_task(self, task_row):
    elapsed_seconds = 0
    if task_row.start_time is not None:
      elapsed_seconds = time.perf_counter() - task_row.start_time

    if self.current_task is task_row:
      self.stop_current_task()

    task_row.destroy()
    self.create_task_row(
        task_row.task_text, self.completed_frame, is_completed=True,
        elapsed_seconds=elapsed_seconds,
    )

  def delete_task(self, task_row):
    if self.current_task is task_row:
      self.stop_current_task()
    task_row.destroy()

  def start_timer(self):
    if self.current_task is None:
      return

    elapsed = time.perf_counter() - self.current_task_started_at
    self.current_task_timer.configure(text=self.format_duration(elapsed))
    self.timer_job = self.after(1000, self.start_timer)

  def update_current_task_display(self):
    if self.current_task is None:
      self.current_task_name.configure(text="없음")
      self.current_task_timer.configure(text="00:00:00")
      return

    self.current_task_name.configure(text=self.current_task.task_text)
    self.current_task_timer.configure(text=self.format_duration(
        time.perf_counter() - self.current_task_started_at
    ))

  def format_duration(self, seconds):
    total_seconds = int(seconds)
    minutes, sec = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


if __name__ == "__main__":
  app = TodoApp()
  app.mainloop()