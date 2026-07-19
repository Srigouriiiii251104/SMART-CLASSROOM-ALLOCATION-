function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (const cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function renderChart(elementId, config) {
    const element = document.getElementById(elementId);
    if (!element || !config) {
        return;
    }
    new Chart(element, config);
}

function getThemePalette() {
    const styles = getComputedStyle(document.documentElement);
    return {
        brand: styles.getPropertyValue("--brand").trim() || "#9b5e40",
        brandRgb: styles.getPropertyValue("--brand-rgb").trim() || "155, 94, 64",
        accent: styles.getPropertyValue("--accent").trim() || "#d5a24c",
        accentRgb: styles.getPropertyValue("--accent-rgb").trim() || "213, 162, 76",
        sage: styles.getPropertyValue("--sage").trim() || "#71876d",
        sageRgb: styles.getPropertyValue("--sage-rgb").trim() || "113, 135, 109",
        sky: styles.getPropertyValue("--sky").trim() || "#7f9dbf",
        skyRgb: styles.getPropertyValue("--sky-rgb").trim() || "127, 157, 191",
        text: styles.getPropertyValue("--text").trim() || "#2e2219",
        muted: styles.getPropertyValue("--muted").trim() || "#6f6154",
        grid: styles.getPropertyValue("--grid-line").trim() || "rgba(113, 84, 58, 0.09)"
    };
}

function getCartesianChartOptions(theme) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: theme.text
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: theme.muted
                },
                grid: {
                    color: theme.grid
                }
            },
            y: {
                ticks: {
                    color: theme.muted
                },
                grid: {
                    color: theme.grid
                }
            }
        }
    };
}

function getRadialChartOptions(theme) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: theme.text
                }
            }
        }
    };
}

function initDashboardCharts() {
    const metricsScript = document.getElementById("dashboard-metrics");
    if (!metricsScript) {
        return;
    }
    const metrics = JSON.parse(metricsScript.textContent);
    const theme = getThemePalette();

    renderChart("attendanceTrendChart", {
        type: "line",
        data: {
            labels: metrics.charts.attendance_trends.labels,
            datasets: [{
                label: "Attendance Checkpoints",
                data: metrics.charts.attendance_trends.data,
                borderColor: theme.brand,
                backgroundColor: `rgba(${theme.brandRgb}, 0.16)`,
                fill: true,
                tension: 0.35
            }]
        },
        options: getCartesianChartOptions(theme)
    });

    renderChart("peakUsageChart", {
        type: "bar",
        data: {
            labels: metrics.charts.peak_usage.labels,
            datasets: [{
                label: "Peak Classroom Usage",
                data: metrics.charts.peak_usage.data,
                backgroundColor: theme.accent
            }]
        },
        options: getCartesianChartOptions(theme)
    });

    renderChart("roomOccupancyChart", {
        type: "doughnut",
        data: {
            labels: metrics.charts.room_occupancy.labels,
            datasets: [{
                data: metrics.charts.room_occupancy.data,
                backgroundColor: [theme.brand, theme.accent, theme.sky, theme.sage, `rgba(${theme.brandRgb}, 0.55)`]
            }]
        },
        options: getRadialChartOptions(theme)
    });

    renderChart("resourceUtilizationChart", {
        type: "pie",
        data: {
            labels: metrics.charts.resource_utilization.labels,
            datasets: [{
                data: metrics.charts.resource_utilization.data,
                backgroundColor: [theme.brand, theme.accent, theme.sky, theme.sage, `rgba(${theme.accentRgb}, 0.7)`]
            }]
        },
        options: getRadialChartOptions(theme)
    });

    renderChart("facultyWorkloadChart", {
        type: "bar",
        data: {
            labels: metrics.charts.faculty_workload.labels,
            datasets: [{
                label: "Sessions",
                data: metrics.charts.faculty_workload.data,
                backgroundColor: theme.sky
            }]
        },
        options: getCartesianChartOptions(theme)
    });

    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach((tabEl) => {
        tabEl.addEventListener('shown.bs.tab', () => {
            if (window.Chart && Chart.instances) {
                Object.values(Chart.instances).forEach(chart => {
                    chart.resize();
                });
            }
        });
    });
}

function initTimetableBoard() {
    const board = document.querySelector("[data-timetable-board='true']");
    if (!board || board.dataset.canManage !== "true") {
        return;
    }

    let draggedEntryId = null;
    const status = document.getElementById("timetableStatus");

    board.querySelectorAll(".schedule-chip").forEach((chip) => {
        chip.addEventListener("dragstart", () => {
            draggedEntryId = chip.dataset.entryId;
        });
    });

    board.querySelectorAll(".drop-cell").forEach((cell) => {
        cell.addEventListener("dragover", (event) => {
            event.preventDefault();
            cell.classList.add("drag-over");
        });

        cell.addEventListener("dragleave", () => cell.classList.remove("drag-over"));
        cell.addEventListener("drop", async (event) => {
            event.preventDefault();
            cell.classList.remove("drag-over");
            if (!draggedEntryId) {
                return;
            }

            const payload = {
                entry_id: draggedEntryId,
                timeslot_id: cell.dataset.timeslotId,
                classroom_id: cell.dataset.classroomId,
            };

            const response = await fetch("/academics/api/timetable/move/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (!response.ok) {
                status.textContent = data.detail || "That move would create a timetable clash.";
                return;
            }
            status.textContent = "Session moved. Refreshing the board...";
            window.location.reload();
        });
    });
}

function appendBubble(chatWindow, text, role) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function initChatbot() {
    const form = document.getElementById("chatbotForm");
    const chatWindow = document.getElementById("chatWindow");
    if (!form || !chatWindow) {
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const input = document.getElementById("chatQuery");
        const query = input.value.trim();
        if (!query) {
            return;
        }
        appendBubble(chatWindow, query, "user");
        input.value = "";

        const response = await fetch("/assistant/api/query/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ query }),
        });
        const data = await response.json();
        appendBubble(chatWindow, data.response || "I could not process that request.", "assistant");
    });

    const voiceBtn = document.getElementById("voiceInputBtn");
    const input = document.getElementById("chatQuery");
    if (voiceBtn && input) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            voiceBtn.style.display = 'none';
        } else {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            voiceBtn.addEventListener("click", () => {
                try {
                    recognition.start();
                    voiceBtn.classList.add("text-danger");
                    voiceBtn.querySelector("i").className = "bi bi-mic-mute-fill";
                    input.placeholder = "Listening...";
                } catch (e) {
                    console.warn(e);
                }
            });

            recognition.onresult = (event) => {
                const speechResult = event.results[0][0].transcript;
                input.value = speechResult;
                form.dispatchEvent(new Event("submit"));
            };

            recognition.onspeechend = () => {
                recognition.stop();
                voiceBtn.classList.remove("text-danger");
                voiceBtn.querySelector("i").className = "bi bi-mic-fill";
                input.placeholder = "Ask the campus assistant...";
            };

            recognition.onerror = (event) => {
                voiceBtn.classList.remove("text-danger");
                voiceBtn.querySelector("i").className = "bi bi-mic-fill";
                input.placeholder = "Error, try again...";
                console.error("Speech recognition error", event.error);
            };
        }
    }
}

function initAttendanceMarking() {
    const button = document.querySelector("[data-attendance-mark='true']");
    const status = document.getElementById("attendanceStatus");
    if (!button || !status) {
        return;
    }

    // helper to show small toasts
    const showToast = (msg, success = true) => {
        const t = document.createElement('div');
        t.className = 'toast ' + (success ? 'toast-success' : 'toast-error');
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(() => t.classList.add('visible'), 10);
        setTimeout(() => { t.classList.remove('visible'); setTimeout(() => t.remove(), 300); }, 3000);
    };

    // disable button if no token
    const setButtonState = (hasToken) => {
        button.disabled = !hasToken;
        button.textContent = hasToken ? 'Mark My Attendance' : 'Waiting for QR';
    };

    setButtonState(Boolean(button.dataset.qrToken));

    button.addEventListener("click", async () => {
        if (!button.dataset.qrToken) {
            showToast('No QR available right now.', false);
            return;
        }
        button.disabled = true;
        const response = await fetch("/attendance/api/mark/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ qr_token: button.dataset.qrToken }),
        });
        const data = await response.json();
        if (response.ok) {
            showToast('Attendance marked. You are checked in.', true);
            status.textContent = 'Attendance marked. You are checked in for this class.';
            // keep button disabled to avoid user spamming; allow re-check if backend allows
            button.disabled = true;
            button.textContent = 'Checked In';
        } else {
            showToast(data.detail || 'Attendance could not be marked.', false);
            status.textContent = data.detail || 'Attendance could not be marked.';
            button.disabled = false;
            button.textContent = 'Mark My Attendance';
        }
    });
}


function initQRGeneration() {
    const genBtn = document.getElementById("generateQrBtn");
    const countdown = document.getElementById("qrCountdown");
    const studentBtn = document.querySelector("[data-attendance-mark='true']");
    if (!genBtn) return;

    genBtn.addEventListener("click", async () => {
        genBtn.disabled = true;
        genBtn.textContent = "Generating...";
        const sessionId = genBtn.dataset.sessionId;
        const response = await fetch("/attendance/api/generate_qr/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ session_id: sessionId, duration: 90 }),
        });
        const data = await response.json();
        if (!response.ok) {
            genBtn.textContent = "Generate QR (retry)";
            genBtn.disabled = false;
            countdown.textContent = data.detail || "Could not generate QR.";
            return;
        }

        // show QR image if available
        if (data.qr_image_url) {
            // prefer modal if present
            const modal = document.getElementById('qrModal');
            const modalImg = document.getElementById('qrModalImg');
            const modalCountdown = document.getElementById('qrModalCountdown');
            if (modal && modalImg) {
                modalImg.src = data.qr_image_url + "?t=" + Date.now();
                modal.style.display = 'flex';
                // close handler
                const closeBtn = document.getElementById('qrModalClose');
                if (closeBtn) closeBtn.onclick = () => { modal.style.display = 'none'; };
                // update countdown reference
                if (modalCountdown) countdown = modalCountdown;
            } else {
                let img = document.querySelector('.qr-preview');
                if (!img) {
                    img = document.createElement('img');
                    img.className = 'qr-preview mt-3';
                    genBtn.parentNode.insertBefore(img, genBtn);
                }
                img.src = data.qr_image_url + "?t=" + Date.now();
            }
        }

        // update student button token and enable it
        if (studentBtn) {
            studentBtn.dataset.qrToken = data.qr_token;
            studentBtn.disabled = false;
            studentBtn.textContent = 'Mark My Attendance';
        }

        // start countdown
        let expiresAt = new Date(data.expires_at);
        const tick = () => {
            const now = new Date();
            const diff = Math.max(0, Math.floor((expiresAt - now) / 1000));
            countdown.textContent = diff > 0 ? `Expires in ${diff}s` : "QR expired";
            if (diff <= 0) {
                genBtn.textContent = "Generate QR";
                genBtn.disabled = false;
                // disable student button when token expired
                if (studentBtn) {
                    studentBtn.dataset.qrToken = '';
                    studentBtn.disabled = true;
                    studentBtn.textContent = 'Waiting for QR';
                }
                // auto-close modal if open
                const modal = document.getElementById('qrModal');
                if (modal) modal.style.display = 'none';
                clearInterval(timer);
            }
        };
        tick();
        const timer = setInterval(tick, 1000);
    });
}

function initQRScanner() {
    const scanBtn = document.getElementById('startScannerBtn');
    const scannerModal = document.getElementById('qrScannerModal');
    const scannerRoot = document.getElementById('qrScannerRoot');
    const scannerStatus = document.getElementById('scannerStatus');
    const closeScannerBtn = document.getElementById('qrScannerClose');
    const attendanceBtn = document.querySelector("[data-attendance-mark='true']");
    if (!scanBtn || !scannerModal || !scannerRoot) {
        return;
    }

    let html5QrCode = null;
    let scanning = false;

    const stopScanning = async () => {
        if (html5QrCode && scanning) {
            try {
                await html5QrCode.stop();
                await html5QrCode.clear();
            } catch (err) {
                console.warn('QR scanner stop error', err);
            }
        }
        scanning = false;
        if (scannerModal) scannerModal.style.display = 'none';
        if (scannerStatus) scannerStatus.textContent = '';
    };

    const parseToken = (decodedText) => {
        const match = /attendance:\d+:([0-9a-fA-F-]+)/.exec(decodedText);
        if (match) {
            return match[1];
        }
        return decodedText.trim();
    };

    const handleScanSuccess = async (decodedText) => {
        const token = parseToken(decodedText);
        if (!token) {
            if (scannerStatus) scannerStatus.textContent = 'Unrecognized QR format.';
            return;
        }
        if (scannerStatus) scannerStatus.textContent = 'QR scanned successfully! Submitting...';
        await stopScanning();
        if (attendanceBtn) {
            attendanceBtn.dataset.qrToken = token;
            attendanceBtn.click();
        }
    };

    scanBtn.addEventListener('click', async () => {
        if (!window.Html5Qrcode) {
            if (scannerStatus) scannerStatus.textContent = 'QR scanning library unavailable.';
            return;
        }
        scannerModal.style.display = 'flex';
        if (scannerStatus) scannerStatus.textContent = 'Starting camera...';
        html5QrCode = new Html5Qrcode('qrScannerRoot');
        try {
            const cameras = await Html5Qrcode.getCameras();
            if (!cameras || cameras.length === 0) {
                if (scannerStatus) scannerStatus.textContent = 'No camera found.';
                return;
            }
            const cameraId = cameras[0].id;
            scanning = true;
            await html5QrCode.start(cameraId, { fps: 10, qrbox: 250 }, handleScanSuccess, (errorMessage) => {
                if (scannerStatus) scannerStatus.textContent = 'Scanning...';
            });
        } catch (err) {
            if (scannerStatus) scannerStatus.textContent = 'Unable to access camera.';
            console.warn('QR scanner start error', err);
        }
    });

    if (closeScannerBtn) {
        closeScannerBtn.addEventListener('click', stopScanning);
    }
}

function initRoleSelectors() {
    document.querySelectorAll("[data-role-selector]").forEach((selector) => {
        const targetInputId = selector.dataset.targetInput;
        const input = document.getElementById(targetInputId);
        const buttons = selector.querySelectorAll("[data-role-value]");
        if (!input || !buttons.length) {
            return;
        }

        const conditionalBlocks = document.querySelectorAll(".role-conditional[data-role-visible]");

        const syncRole = (roleValue) => {
            input.value = roleValue;
            buttons.forEach((button) => {
                button.classList.toggle("is-active", button.dataset.roleValue === roleValue);
            });
            conditionalBlocks.forEach((block) => {
                const shouldShow = block.dataset.roleVisible === roleValue;
                block.classList.toggle("is-hidden", !shouldShow);
            });
        };

        const initialRole = input.value || buttons[0].dataset.roleValue;
        syncRole(initialRole);

        buttons.forEach((button) => {
            button.addEventListener("click", () => syncRole(button.dataset.roleValue));
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initDashboardCharts();
    initTimetableBoard();
    initChatbot();
    initAttendanceMarking();
    initQRGeneration();
    initQRScanner();
    initRoleSelectors();
});
