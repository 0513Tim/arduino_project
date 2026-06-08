import threading
import tkinter as tk
from tkinter import messagebox

import requests


API_BASE_URL = "http://127.0.0.1:8000"
SEAT_STATUS_MAP = {
    "empty": ("#3cb371", "空位"),
    "using": ("#dc3545", "使用中"),
    "reserved": ("#ffb703", "已預約"),
    "away": ("#fb8500", "暫時離席"),
}


class StudyRoomGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("智慧自習室系統")
        self.root.geometry("760x620")
        self.root.configure(bg="#f4f6fb")

        self.student_id_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.login_text_var = tk.StringVar(value="尚未登入")
        self.selected_seat_var = tk.StringVar(value="目前選擇座位：無")
        self.noise_text_var = tk.StringVar(value="目前噪音：尚無資料")
        self.login_student_name = None
        self.selected_seat = None

        self.seat_buttons = {}
        self.seat_status_labels = {}

        self._build_layout()
        self._start_auto_refresh()

    def _build_layout(self):
        title = tk.Label(
            self.root,
            text="智慧自習室系統",
            font=("Helvetica", 22, "bold"),
            bg="#f4f6fb",
            fg="#1f2a44",
        )
        title.pack(pady=12)

        self._build_login_frame()
        self._build_seat_frame()
        self._build_control_frame()
        self._build_status_frame()
        self._build_noise_frame()

    def _build_login_frame(self):
        login_frame = tk.LabelFrame(self.root, text="登入區", padx=12, pady=12, bg="white", fg="#333")
        login_frame.pack(fill="x", padx=20, pady=8)

        tk.Label(login_frame, text="學號", bg="white").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        tk.Entry(login_frame, textvariable=self.student_id_var, width=18).grid(row=0, column=1, padx=6, pady=6)

        tk.Label(login_frame, text="密碼", bg="white").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        tk.Entry(login_frame, textvariable=self.password_var, width=18, show="*").grid(row=0, column=3, padx=6, pady=6)

        tk.Button(login_frame, text="登入", command=self.login, width=10, bg="#2f80ed", fg="white").grid(
            row=0, column=4, padx=8, pady=6
        )

        tk.Label(login_frame, textvariable=self.login_text_var, bg="white", fg="#555").grid(
            row=1, column=0, columnspan=5, sticky="w", padx=6, pady=4
        )

    def _build_seat_frame(self):
        seat_frame = tk.LabelFrame(self.root, text="座位狀態區", padx=12, pady=12, bg="white")
        seat_frame.pack(fill="x", padx=20, pady=8)

        for index, seat_id in enumerate(["01", "02", "03", "04"]):
            button = tk.Button(
                seat_frame,
                text=f"座位 {seat_id}",
                width=16,
                height=3,
                bg="#3cb371",
                fg="white",
                command=lambda sid=seat_id: self.select_seat(sid),
            )
            button.grid(row=0, column=index, padx=8, pady=6)
            self.seat_buttons[seat_id] = button

            status_label = tk.Label(seat_frame, text="空位", bg="white", fg="#333")
            status_label.grid(row=1, column=index, padx=8, pady=4)
            self.seat_status_labels[seat_id] = status_label

        select_label = tk.Label(seat_frame, textvariable=self.selected_seat_var, bg="white", fg="#1f2a44", font=("Helvetica", 12))
        select_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=8, pady=8)

    def _build_control_frame(self):
        control_frame = tk.LabelFrame(self.root, text="操作區", padx=12, pady=12, bg="white")
        control_frame.pack(fill="x", padx=20, pady=8)

        tk.Button(control_frame, text="重新整理座位", command=self.refresh_seats, width=16).grid(row=0, column=0, padx=8, pady=6)
        tk.Button(control_frame, text="更新噪音", command=self.refresh_noise, width=16).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(control_frame, text="直接離席", command=self.leave, width=16, bg="#ef4444", fg="white").grid(row=0, column=2, padx=8, pady=6)

    def _build_status_frame(self):
        status_frame = tk.LabelFrame(self.root, text="操作訊息", padx=12, pady=12, bg="white")
        status_frame.pack(fill="both", expand=True, padx=20, pady=8)

        self.status_text = tk.Text(status_frame, height=10, state="disabled", bg="#f8fafc")
        self.status_text.pack(fill="both", expand=True)

    def _build_noise_frame(self):
        noise_frame = tk.LabelFrame(self.root, text="噪音顯示", padx=12, pady=12, bg="white")
        noise_frame.pack(fill="x", padx=20, pady=8)

        tk.Label(noise_frame, textvariable=self.noise_text_var, bg="white", fg="#1f2a44", font=("Helvetica", 12, "bold")).pack(anchor="w")

    def _start_auto_refresh(self):
        self.refresh_seats()
        self.refresh_noise()
        self.root.after(3000, self._start_auto_refresh)

    def _run_in_thread(self, target):
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def login(self):
        student_id = self.student_id_var.get().strip()
        password = self.password_var.get().strip()
        if not student_id or not password:
            messagebox.showwarning("提醒", "請輸入學號與密碼")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"student_id": student_id, "password": password},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            messagebox.showerror("登入失敗", f"無法連線到後端：\n{exc}")
            return

        if not data.get("success"):
            messagebox.showerror("登入失敗", data.get("message", "帳號或密碼錯誤"))
            self.login_text_var.set("登入失敗")
            return

        student = data.get("student", {})
        self.login_student_name = student.get("name")
        self.login_text_var.set(f"已登入: {student.get('student_id')} {self.login_student_name}")
        self.append_status(f"登入成功：{student.get('student_id')} {self.login_student_name}")

    def select_seat(self, seat_id: str):
        self.selected_seat = seat_id
        self.selected_seat_var.set(f"目前選擇座位：{seat_id}")
        self.append_status(f"已選擇座位：{seat_id}")

    def leave(self):
        if not self.selected_seat:
            messagebox.showwarning("提醒", "請先選擇座位")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/leave",
                json={"seat_id": self.selected_seat},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            messagebox.showerror("離席失敗", f"無法連線到後端：\n{exc}")
            return

        if not data.get("success"):
            messagebox.showerror("離席失敗", data.get("message", "離席失敗"))
            return

        self.append_status(f"離席成功：{self.selected_seat}")
        self.refresh_seats()

    def refresh_seats(self):
        def _task():
            try:
                response = requests.get(f"{API_BASE_URL}/seats", timeout=5)
                response.raise_for_status()
                seats = response.json()
            except requests.RequestException as exc:
                self.root.after(0, lambda: self.append_status(f"查詢座位失敗：{exc}"))
                return

            def _update():
                for seat in seats:
                    seat_id = seat.get("seat_id")
                    status = seat.get("status", "empty")
                    color, label_text = SEAT_STATUS_MAP.get(status, ("#9e9e9e", status))
                    if seat_id in self.seat_buttons:
                        self.seat_buttons[seat_id].config(bg=color)
                    if seat_id in self.seat_status_labels:
                        self.seat_status_labels[seat_id].config(text=label_text)
                self.append_status("座位狀態已更新。", clear=False)

            self.root.after(0, _update)

        self._run_in_thread(_task)

    def refresh_noise(self):
        def _task():
            try:
                response = requests.get(f"{API_BASE_URL}/latest_noise", timeout=5)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException:
                self.root.after(0, lambda: self.noise_text_var.set("目前噪音：尚無資料"))
                return

            seat_id = data.get("seat_id", "?")
            noise_value = data.get("noise_value", "?")
            warning = data.get("is_warning", False)
            status_text = "噪音警告" if warning else "正常"
            self.root.after(0, lambda: self.noise_text_var.set(f"目前噪音：座位 {seat_id} / 數值 {noise_value} / {status_text}"))

        self._run_in_thread(_task)

    def append_status(self, message: str, clear: bool = True):
        self.status_text.config(state="normal")
        if clear:
            self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    StudyRoomGUI(root)
    root.mainloop()
