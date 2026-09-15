import time
from datetime import datetime
import customtkinter as ctk


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class TodoApp(ctk.CTk):

  def __init__(self):
    super().__init__()

    # 1. 창 기본 설정
    self.title("나의 할 일 목록 (To-Do List)")
    self.geometry("390x720")
    self.resizable(False, False)
    self.configure(fg_color="#070D18")

    # 2. 메인 타이틀 라벨
    self.title_label = ctk.CTkLabel(
      self, text="TASK // LOCK", font=ctk.CTkFont(size=22, weight="bold"),
      text_color="#7DF9FF",
    )
    self.title_label.pack(pady=(14, 5))

    self.clock_label = ctk.CTkLabel(
      self, text="", font=ctk.CTkFont(size=13), text_color="#8EA7C4"
    )
    self.clock_label.pack(pady=(0, 7))

    self.lock_schedules = []
    self.cancelled_lock_schedule = None
    self.active_lock_schedule = None
    self.lock_settings_frame = ctk.CTkFrame(
        self, fg_color="#101B2D", border_width=1, border_color="#23415F", corner_radius=14
    )
    self.lock_settings_frame.pack(fill="x", padx=14, pady=(0, 7))
    ctk.CTkLabel(
      self.lock_settings_frame, text="할 일 및 잠금 예약", font=ctk.CTkFont(size=15, weight="bold"),
      text_color="#D7F9FF"
    ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")
    ctk.CTkLabel(self.lock_settings_frame, text="일정 이름").grid(row=1, column=0, padx=(10, 4), pady=8)
    self.lock_name_entry = ctk.CTkEntry(
      self.lock_settings_frame, width=125, placeholder_text="공부 시간",
      fg_color="#081321", border_color="#2A5875"
    )
    self.lock_name_entry.grid(row=1, column=1, padx=4, pady=8)
    ctk.CTkLabel(self.lock_settings_frame, text="시작").grid(row=2, column=0, padx=(10, 4), pady=8)
    self.lock_start_entry = ctk.CTkEntry(
      self.lock_settings_frame, width=65, placeholder_text="22:00",
      fg_color="#081321", border_color="#2A5875"
    )
    self.lock_start_entry.insert(0, "22:00")
    self.lock_start_entry.grid(row=2, column=1, padx=4, pady=8)
    ctk.CTkLabel(self.lock_settings_frame, text="종료").grid(row=2, column=2, padx=4, pady=8)
    self.lock_end_entry = ctk.CTkEntry(
      self.lock_settings_frame, width=65, placeholder_text="07:00",
      fg_color="#081321", border_color="#2A5875"
    )
    self.lock_end_entry.insert(0, "07:00")
    self.lock_end_entry.grid(row=2, column=3, padx=(4, 10), pady=8)
    self.lock_enabled = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(
      self.lock_settings_frame, text="일정 잠금 사용", variable=self.lock_enabled,
      command=self.check_lock_schedule,
    ).grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
    ctk.CTkButton(
      self.lock_settings_frame, text="예약 추가", width=75, command=self.add_lock_schedule,
      fg_color="#00B8D4", hover_color="#00E5FF", text_color="#06111F",
    ).grid(row=3, column=3, padx=(4, 10), pady=(0, 10))
    self.lock_status_label = ctk.CTkLabel(
      self.lock_settings_frame, text="잠금 기능 꺼짐", text_color="#7187A3"
    )
    self.lock_status_label.grid(row=4, column=0, columnspan=4, padx=10, pady=(0, 8), sticky="w")
    self.schedule_list_frame = ctk.CTkScrollableFrame(
      self.lock_settings_frame, height=45, fg_color="#0A1422"
    )
    self.schedule_list_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")

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

    # 4. 할 일 목록 섹션
    self.active_title = ctk.CTkLabel(
        self, text="할 일 목록", font=ctk.CTkFont(size=16, weight="bold")
    )
    self.active_title.pack(anchor="w", padx=20, pady=(10, 5))

    self.active_frame = ctk.CTkScrollableFrame(self, width=340, height=60)
    self.active_frame.pack(padx=20, pady=(0, 10), fill="x")
    self.input_frame.pack_forget()
    self.active_title.pack_forget()
    self.active_frame.pack_forget()

    # 5. 완료한 일정 섹션
    self.completed_title = ctk.CTkLabel(
      self, text="완료한 일정", font=ctk.CTkFont(size=15, weight="bold"),
      text_color="#D7F9FF"
    )
    self.completed_title.pack(anchor="w", padx=14, pady=(5, 4))

    self.completed_frame = ctk.CTkScrollableFrame(
      self, width=350, height=120, fg_color="#0A1422",
      border_width=1, border_color="#1B334E"
    )
    self.completed_frame.pack(padx=14, pady=(0, 10), fill="x")

    self.current_task = None
    self.current_task_started_at = None
    self.timer_job = None
    self.clock_job = None
    self.lock_overlay = None
    self.active_lock_schedule = None
    self.active_lock_started_at = None
    self.update_clock()

  def add_task(self):
    task_text = self.entry.get().strip()
    if not task_text:
      return

    self.create_task_row(task_text, self.active_frame)
    self.entry.delete(0, "end")

  def update_clock(self):
    now = datetime.now()
    self.clock_label.configure(text=now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초"))
    self.check_lock_schedule()
    self.clock_job = self.after(1000, self.update_clock)

  def add_lock_schedule(self):
    try:
      name = self.lock_name_entry.get().strip()
      start_text = self.lock_start_entry.get().strip()
      end_text = self.lock_end_entry.get().strip()
      if not name:
        raise ValueError
      datetime.strptime(start_text, "%H:%M")
      datetime.strptime(end_text, "%H:%M")
    except ValueError:
      self.lock_status_label.configure(text="일정 이름과 시간(HH:MM)을 입력하세요.", text_color="#D32F2F")
      self.lock_enabled.set(False)
      return

    schedule = (name, start_text, end_text)
    if schedule not in self.lock_schedules:
      self.lock_schedules.append(schedule)
      self.refresh_schedule_list()
    self.lock_enabled.set(True)
    self.lock_status_label.configure(text="잠금 예약이 추가되었습니다.", text_color="#2E7D32")
    self.check_lock_schedule()

  def refresh_schedule_list(self):
    for child in self.schedule_list_frame.winfo_children():
      child.destroy()

    for index, (name, start, end) in enumerate(self.lock_schedules):
      ctk.CTkLabel(
        self.schedule_list_frame, text=f"{name}  |  {start} - {end}",
        text_color="#B8D9E6"
      ).grid(
          row=index, column=0, padx=5, pady=2, sticky="w"
      )
      ctk.CTkButton(
        self.schedule_list_frame, text="삭제", width=45,
        fg_color="#16334B", hover_color="#E0528B", text_color="#D7F9FF",
          command=lambda schedule=(name, start, end): self.remove_lock_schedule(schedule),
      ).grid(row=index, column=1, padx=5, pady=2, sticky="e")

  def remove_lock_schedule(self, schedule):
    if self.active_lock_schedule == schedule:
      self.active_lock_schedule = None
    if schedule in self.lock_schedules:
      self.lock_schedules.remove(schedule)
    if self.cancelled_lock_schedule == schedule:
      self.cancelled_lock_schedule = None
    self.refresh_schedule_list()
    if not self.lock_schedules:
      self.lock_enabled.set(False)
    self.check_lock_schedule()

  def get_active_lock_schedule(self):
    if not self.lock_enabled.get():
      return None

    current = datetime.now().time()
    for name, start_text, end_text in self.lock_schedules:
      start = datetime.strptime(start_text, "%H:%M").time()
      end = datetime.strptime(end_text, "%H:%M").time()
      if start == end or (start < end and start <= current < end) or (start > end and (current >= start or current < end)):
        return name, start_text, end_text
    return None

  def is_lock_time(self):
    active_schedule = self.get_active_lock_schedule()
    if active_schedule is None:
      self.cancelled_lock_schedule = None
      return False
    if active_schedule == self.cancelled_lock_schedule:
      return False
    return True

  def check_lock_schedule(self):
    current_schedule = self.get_active_lock_schedule()
    if self.active_lock_schedule is not None and self.active_lock_schedule != current_schedule:
      finished_schedule = self.active_lock_schedule
      self.active_lock_schedule = None
      elapsed_seconds = time.perf_counter() - self.active_lock_started_at
      self.active_lock_started_at = None
      if finished_schedule != self.cancelled_lock_schedule:
        self.complete_lock_schedule(finished_schedule, elapsed_seconds)

    if current_schedule is not None and current_schedule != self.cancelled_lock_schedule:
      if self.active_lock_schedule != current_schedule:
        self.active_lock_schedule = current_schedule
        self.active_lock_started_at = time.perf_counter()

    if self.is_lock_time():
      self.show_lock_overlay()
      self.lock_status_label.configure(text="잠금 시간입니다.", text_color="#D32F2F")
    else:
      self.hide_lock_overlay()
      if self.lock_enabled.get():
        self.lock_status_label.configure(text="잠금 일정 대기 중", text_color="#2E7D32")

  def complete_lock_schedule(self, schedule, elapsed_seconds):
    if schedule not in self.lock_schedules:
      return

    self.lock_schedules.remove(schedule)
    self.refresh_schedule_list()
    self.create_task_row(
      schedule[0], self.completed_frame, is_completed=True,
      elapsed_seconds=elapsed_seconds,
    )
    self.lock_status_label.configure(text=f"'{schedule[0]}' 일정 완료", text_color="#7DF9FF")
    if not self.lock_schedules:
      self.lock_enabled.set(False)

  def show_lock_overlay(self):
    if self.lock_overlay is not None and self.lock_overlay.winfo_exists():
      return

    self.lock_overlay = ctk.CTkFrame(self, fg_color="#050A14", corner_radius=0)
    self.lock_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    ctk.CTkLabel(
        self.lock_overlay, text="앱 잠금 중", font=ctk.CTkFont(size=28, weight="bold"),
      text_color="#7DF9FF",
    ).pack(pady=(300, 15))
    active_schedule = self.get_active_lock_schedule()
    if active_schedule is not None:
      ctk.CTkLabel(
        self.lock_overlay, text=active_schedule[0],
        font=ctk.CTkFont(size=18, weight="bold"), text_color="#F06FAE",
      ).pack(pady=(0, 10))
    ctk.CTkLabel(
        self.lock_overlay, text="설정한 종료 시간이 되면 자동으로 해제됩니다.",
      text_color="#8EA7C4",
    ).pack()
    ctk.CTkButton(
        self.lock_overlay, text="이번 잠금 취소", width=130,
      fg_color="#16334B", hover_color="#E0528B", text_color="#D7F9FF",
      command=self.cancel_current_lock,
    ).pack(pady=20)
    self.lock_overlay.lift()

  def cancel_current_lock(self):
    self.cancelled_lock_schedule = self.get_active_lock_schedule()
    self.hide_lock_overlay()
    self.lock_status_label.configure(text="이번 잠금을 취소했습니다.", text_color="#F57C00")

  def hide_lock_overlay(self):
    if self.lock_overlay is not None and self.lock_overlay.winfo_exists():
      self.lock_overlay.destroy()
    self.lock_overlay = None

  def create_task_row(self, task_text, parent, is_completed=False, elapsed_seconds=0):
    task_row = ctk.CTkFrame(parent)
    task_row.pack(fill="x", pady=5, padx=5)
    task_row.task_text = task_text
    task_row.start_time = None
    task_row.elapsed_seconds = elapsed_seconds

    task_label = ctk.CTkLabel(
      task_row, text=task_text, font=("맑은 고딕", 13), anchor="w",
      text_color="#D7F9FF" if is_completed else "#FFFFFF"
    )
    task_label.pack(side="left", padx=10, pady=8, expand=True, fill="x")

    if is_completed:
      task_row.configure(
        fg_color="#101F34", border_width=1, border_color="#234F6B", corner_radius=10
      )
      duration_label = ctk.CTkLabel(
          task_row,
          text=f"소요시간: {self.format_duration(elapsed_seconds)}",
          font=("맑은 고딕", 11, "bold"),
        text_color="#7DF9FF",
      )
      duration_label.pack(side="right", padx=(0, 10), pady=8)

      delete_button = ctk.CTkButton(
          task_row,
          text="삭제",
          width=50,
          fg_color="#16334B",
          hover_color="#E0528B",
          text_color="#D7F9FF",
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