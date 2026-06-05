import tkinter as tk
from tkinter import messagebox

import requests


API_BASE_URL = "http://127.0.0.1:8000"
SEAT_COLORS = {
    "available": "#3cb371",
    "using": "#dc3545",
    "warning": "#ff9800",
    "away": "#9e9e9e",
    "reserved": "#6c757d",
}


class StudyRoomGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("智慧自習室系統")
        self.root.geometry("760x560")
        self.root.configure(bg="#f4f6fb")

        self.student_id_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.noise_var = tk.StringVar(value="目前噪音: 尚無資料")
        self.current_student_id = None
        self.current_student_name = None
        self.seat_buttons = {}
        self.status_labels = {}

        self._build_layout()
        self.refresh_seats()
        self.refresh_noise()

    def _build_layout(self):
        title = tk.Label(
            self.root,
            text="智慧自習室 NFC 劃位與噪音預警",
            font=("Helvetica", 20, "bold"),
            bg="#f4f6fb",
            fg="#1f2a44",
        )
        title.pack(pady=16)

        login_frame = tk.LabelFrame(self.root, text="登入區", padx=12, pady=12, bg="white")
        login_frame.pack(fill="x", padx=20, pady=8)

        tk.Label(login_frame, text="學號", bg="white").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        tk.Entry(login_frame, textvariable=self.student_id_var, width=18).grid(row=0, column=1, padx=6, pady=4)
        tk.Label(login_frame, text="密碼", bg="white").grid(row=0, column=2, padx=6, pady=4, sticky="w")
        tk.Entry(login_frame, textvariable=self.password_var, width=18, show="*").grid(row=0, column=3, padx=6, pady=4)
        tk.Button(login_frame, text="登入", command=self.login, width=10, bg="#2f80ed", fg="white").grid(
            row=0, column=4, padx=8, pady=4
        )

        self.login_status_label = tk.Label(login_frame, text="尚未登入", bg="white", fg="#555")
        self.login_status_label.grid(row=1, column=0, columnspan=5, sticky="w", padx=6, pady=6)

        seats_frame = tk.LabelFrame(self.root, text="選位區", padx=12, pady=12, bg="white")
        seats_frame.pack(fill="x", padx=20, pady=8)

        for index, seat_no in enumerate(range(1, 5)):
            seat_text = f"座位 {seat_no:02d}"
            button = tk.Button(
                seats_frame,
                text=seat_text,
                width=14,
                height=2,
                bg="#3cb371",
                fg="white",
                command=lambda value=seat_no: self.checkin(value),
            )
            button.grid(row=0, column=index, padx=8, pady=6)
            self.seat_buttons[seat_no] = button

            label = tk.Label(seats_frame, text="available", bg="white", fg="#333")
            label.grid(row=1, column=index, padx=8, pady=4)
            self.status_labels[seat_no] = label

        control_frame = tk.LabelFrame(self.root, text="操作區", padx=12, pady=12, bg="white")
        control_frame.pack(fill="x", padx=20, pady=8)

        tk.Button(control_frame, text="查詢座位", command=self.refresh_seats, width=14).grid(row=0, column=0, padx=8, pady=6)
        tk.Button(control_frame, text="查詢噪音", command=self.refresh_noise, width=14).grid(row=0, column=1, padx=8, pady=6)
        tk.Button(control_frame, text="直接離席", command=self.leave, width=14, bg="#ef4444", fg="white").grid(
            row=0, column=2, padx=8, pady=6
        )

        status_frame = tk.LabelFrame(self.root, text="狀態區", padx=12, pady=12, bg="white")
        status_frame.pack(fill="both", expand=True, padx=20, pady=8)

        self.status_text = tk.Text(status_frame, height=10, width=80, state="disabled", bg="#f8fafc")
        self.status_text.pack(fill="both", expand=True)

        noise_frame = tk.LabelFrame(self.root, text="噪音區", padx=12, pady=12, bg="white")
        noise_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(noise_frame, textvariable=self.noise_var, bg="white", fg="#1f2a44", font=("Helvetica", 12, "bold")).pack(
            anchor="w"
        )

    def login(self):
        payload = {
            "student_id": self.student_id_var.get().strip(),
            "password": self.password_var.get().strip(),
        }
        if not payload["student_id"] or not payload["password"]:
            messagebox.showwarning("提醒", "請輸入學號與密碼")
            return

        try:
            response = requests.post(f"{API_BASE_URL}/login", json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            messagebox.showerror("登入失敗", f"無法連線到 API:\n{exc}")
            return

        self.current_student_id = data["student_id"]
        self.current_student_name = data["name"]
        self.login_status_label.config(text=f"已登入: {self.current_student_name} ({self.current_student_id})", fg="#166534")
        self.append_status(f"登入成功: {self.current_student_id} {self.current_student_name}")

    def checkin(self, seat_no: int):
        if not self.current_student_id:
            messagebox.showwarning("提醒", "請先登入")
            return

        nfc_map = {
            "111410001": "A35F2911",
            "111410002": "B24C8832",
            "111410003": "C91D782A",
        }
        payload = {
            "nfc_uid": nfc_map.get(self.current_student_id, ""),
            "seat_no": seat_no,
        }
        if not payload["nfc_uid"]:
            messagebox.showerror("報到失敗", "找不到對應的 NFC UID")
            return

        try:
            response = requests.post(f"{API_BASE_URL}/checkin", json=payload, timeout=5)
            if response.status_code >= 400:
                detail = response.json().get("detail", "unknown error")
                raise requests.HTTPError(detail)
        except requests.RequestException as exc:
            messagebox.showerror("報到失敗", str(exc))
            return

        self.append_status(f"座位 {seat_no:02d} 報到成功")
        self.refresh_seats()

    def leave(self):
        if not self.current_student_id:
            messagebox.showwarning("提醒", "請先登入")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/leave",
                json={"student_id": self.current_student_id},
                timeout=5,
            )
            if response.status_code >= 400:
                detail = response.json().get("detail", "unknown error")
                raise requests.HTTPError(detail)
        except requests.RequestException as exc:
            messagebox.showerror("離席失敗", str(exc))
            return

        self.append_status(f"{self.current_student_id} 已直接離席")
        self.refresh_seats()

    def refresh_seats(self):
        try:
            response = requests.get(f"{API_BASE_URL}/seats", timeout=5)
            response.raise_for_status()
            seats = response.json()
        except requests.RequestException as exc:
            self.append_status(f"查詢座位失敗: {exc}")
            return

        lines = []
        for seat in seats:
            seat_no = seat["seat_no"]
            status = seat["status"]
            student_id = seat["student_id"] or "-"
            self.seat_buttons[seat_no].config(bg=SEAT_COLORS.get(status, "#9e9e9e"))
            self.status_labels[seat_no].config(text=status)
            lines.append(f"座位 {seat_no:02d}: {status} / student_id={student_id}")
        self.append_status("\n".join(lines))

    def refresh_noise(self):
        try:
            response = requests.get(f"{API_BASE_URL}/noise/latest", timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            self.noise_var.set("目前噪音: 尚無資料")
            return

        self.noise_var.set(
            f"目前噪音: 座位 {data['seat_no']} / 數值 {data['noise_value']} / 狀態 {data['level']}"
        )

    def append_status(self, message: str, clear: bool = True):
        self.status_text.config(state="normal")
        if clear:
            self.status_text.delete("1.0", tk.END)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.config(state="disabled")


if __name__ == "__main__":
    window = tk.Tk()
    app = StudyRoomGUI(window)
    window.mainloop()
