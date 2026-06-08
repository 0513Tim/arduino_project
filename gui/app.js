const API_BASE_URL = "http://127.0.0.1:8000";
let selectedSeat = null;
let currentStudent = null;

const loginForm = document.querySelector("#login-form");
const studentIdInput = document.querySelector("#student-id");
const passwordInput = document.querySelector("#password");
const loginMessage = document.querySelector("#login-message");
const loginName = document.querySelector("#login-name");
const seatGrid = document.querySelector("#seat-grid");
const selectedSeatLabel = document.querySelector("#selected-seat");
const noiseSeat = document.querySelector("#noise-seat");
const noiseValue = document.querySelector("#noise-value");
const noiseStatus = document.querySelector("#noise-status");
const refreshSeatsButton = document.querySelector("#refresh-seats");
const refreshNoiseButton = document.querySelector("#refresh-noise");
const leaveButton = document.querySelector("#leave-button");

const STATUS_LABELS = {
  empty: { text: "空位", className: "status-empty" },
  using: { text: "使用中", className: "status-using" },
  reserved: { text: "已預約", className: "status-reserved" },
  away: { text: "暫時離席", className: "status-away" },
};

function setMessage(text, type = "error") {
  loginMessage.textContent = text;
  loginMessage.style.color = type === "success" ? "#16a34a" : "#dc2626";
}

function updateSelectedSeat(seatId) {
  selectedSeat = seatId;
  selectedSeatLabel.textContent = `目前選擇座位：${seatId}`;
}

function clearSelectedSeat() {
  selectedSeat = null;
  selectedSeatLabel.textContent = "目前選擇座位：無";
}

function renderSeats(seats) {
  seatGrid.innerHTML = "";

  seats.forEach((seat) => {
    const seatId = seat.seat_id;
    const status = seat.status || "other";
    const studentId = seat.student_id || "無";

    const card = document.createElement("div");
    card.className = `seat-item ${STATUS_LABELS[status]?.className || "status-other"}`;
    card.dataset.seatId = seatId;

    if (selectedSeat === seatId) {
      card.classList.add("selected");
    }

    card.innerHTML = `
      <div class="status-label">${STATUS_LABELS[status]?.text || "未知"}</div>
      <h3>座位 ${seatId}</h3>
      <p>使用者：${studentId}</p>
    `;

    card.addEventListener("click", () => {
      updateSelectedSeat(seatId);
      document.querySelectorAll(".seat-item").forEach((item) => item.classList.remove("selected"));
      card.classList.add("selected");
    });

    seatGrid.appendChild(card);
  });
}

async function fetchSeats() {
  try {
    const response = await fetch(`${API_BASE_URL}/seats`);
    if (!response.ok) {
      throw new Error("無法取得座位狀態");
    }
    const data = await response.json();
    renderSeats(data);
  } catch (error) {
    setMessage(error.message || "取得座位失敗");
  }
}

async function fetchLatestNoise() {
  try {
    const response = await fetch(`${API_BASE_URL}/latest_noise`);
    if (!response.ok) {
      throw new Error("無法取得噪音資料");
    }
    const data = await response.json();
    noiseSeat.textContent = data.seat_id || "-";
    noiseValue.textContent = data.noise_value || "-";
    const warning = data.is_warning;
    noiseStatus.textContent = warning ? "噪音警告" : "正常";
    noiseStatus.className = warning ? "noise-status noise-warning" : "noise-status noise-ok";
  } catch (error) {
    noiseSeat.textContent = "-";
    noiseValue.textContent = "-";
    noiseStatus.textContent = "尚無資料";
    noiseStatus.className = "noise-status";
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMessage("");
  loginName.textContent = "";

  const payload = {
    student_id: studentIdInput.value.trim(),
    password: passwordInput.value.trim(),
  };

  if (!payload.student_id || !payload.password) {
    setMessage("請輸入學號與密碼");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok || data.success === false) {
      setMessage(data.message || "登入失敗");
      return;
    }

    currentStudent = data.student;
    loginName.textContent = `已登入：${currentStudent.student_id} ${currentStudent.name}`;
    setMessage("登入成功", "success");
  } catch (error) {
    setMessage(error.message || "登入錯誤");
  }
});

refreshSeatsButton.addEventListener("click", () => {
  fetchSeats();
});

refreshNoiseButton.addEventListener("click", () => {
  fetchLatestNoise();
});

leaveButton.addEventListener("click", async () => {
  if (!selectedSeat) {
    setMessage("請先選擇座位");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/leave`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seat_id: selectedSeat }),
    });
    const data = await response.json();

    if (!response.ok || data.success === false) {
      setMessage(data.message || "離席失敗");
      return;
    }

    setMessage("離席成功", "success");
    fetchSeats();
  } catch (error) {
    setMessage(error.message || "離席錯誤");
  }
});

function startAutoRefresh() {
  fetchSeats();
  fetchLatestNoise();
  setInterval(() => {
    fetchSeats();
    fetchLatestNoise();
  }, 3000);
}

startAutoRefresh();
