const business = {
  phone: "6281234567890",
  mapsUrl: "https://www.google.com/maps/search/?api=1&query=Gedung+Zubair+205%2C+Universitas+Darussalam+Gontor%2C+Ponorogo",
};

const services = [
  ["Laptop", "Servis hardware, software, masalah layar, baterai, panas, dan performa laptop.", "Periksa laptop"],
  ["PC & Komputer", "Diagnosa PC tidak menyala, lambat, hang, upgrade komponen, dan perawatan berkala.", "Konsultasi PC"],
  ["HP", "Bantuan pengecekan kendala perangkat HP, software, dan fungsi dasar perangkat.", "Tanya layanan HP"],
  ["Printer", "Troubleshooting printer error, hasil cetak bermasalah, koneksi, dan perawatan dasar.", "Tanya layanan printer"],
];

const problems = [
  ["Laptop Lemot", "Performa lambat perlu diperiksa untuk mengetahui langkah penanganan yang sesuai.", "Halo UTC, laptop saya terasa lambat. Saya ingin konsultasi untuk pengecekan."],
  ["Tidak Bisa Menyala", "Perangkat yang tidak menyala perlu diperiksa untuk mengetahui sumber kendalanya.", "Halo UTC, perangkat saya tidak bisa menyala. Saya ingin konsultasi untuk pengecekan."],
  ["Sering Overheat", "Panas berlebih dapat dipengaruhi kondisi perangkat dan perlu pemeriksaan lebih lanjut.", "Halo UTC, perangkat saya sering panas atau overheat. Saya ingin konsultasi untuk pengecekan."],
  ["Windows Bermasalah", "Masalah sistem dapat memengaruhi penggunaan sehari-hari dan perlu dicek terlebih dahulu.", "Halo UTC, Windows di perangkat saya bermasalah. Saya ingin konsultasi untuk pengecekan."],
  ["Mau Upgrade SSD / RAM", "Kompatibilitas perangkat perlu diperiksa sebelum menentukan komponen yang tepat.", "Halo UTC, saya ingin upgrade SSD atau RAM. Bisa bantu cek kompatibilitas perangkat saya?"],
  ["PC Sering Hang", "Hang dapat terjadi karena berbagai kondisi yang perlu diperiksa pada perangkat.", "Halo UTC, PC saya sering hang. Saya ingin konsultasi untuk pengecekan."],
  ["Printer Error", "Kendala cetak, koneksi, atau pesan error dapat disampaikan sebagai informasi awal pemeriksaan.", "Halo UTC, printer saya mengalami error. Saya ingin konsultasi untuk pengecekan."],
  ["HP Bermasalah", "Sampaikan gejala yang terjadi agar UTC dapat mengarahkan langkah konsultasi awal.", "Halo UTC, HP saya bermasalah. Saya ingin konsultasi untuk pengecekan."],
];

function createWhatsAppLink(message) {
  return `https://wa.me/${business.phone}?text=${encodeURIComponent(message)}`;
}

document.querySelector("#service-grid").innerHTML = services.map(([name, description, cta], index) => `
  <article class="service-card reveal">
    <span class="service-number">0${index + 1}</span><h3>${name}</h3><p>${description}</p>
    <a class="service-link wa-link" data-message="Halo UTC, saya ingin konsultasi layanan ${name}." href="#kontak">${cta} <span aria-hidden="true">-&gt;</span></a>
  </article>`).join("");

document.querySelector("#problem-picker").innerHTML = problems.map(([name], index) => `<button class="problem-button" type="button" data-problem="${index}"><span>${name}</span><b aria-hidden="true">+</b></button>`).join("");

document.addEventListener("click", (event) => {
  const problemButton = event.target.closest("[data-problem]");
  if (problemButton) {
    const [name, description, message] = problems[problemButton.dataset.problem];
    document.querySelectorAll(".problem-button").forEach((button) => button.classList.toggle("active", button === problemButton));
    document.querySelector("#problem-result").innerHTML = `<p class="result-kicker">Kemungkinan penanganan</p><h3>${name}</h3><p>${description}</p><a class="button button-small" href="${createWhatsAppLink(message)}" target="_blank" rel="noopener">Konsultasikan masalah ini -&gt;</a>`;
  }
});

document.querySelectorAll(".wa-link").forEach((link) => {
  link.href = createWhatsAppLink(link.dataset.message);
  link.target = "_blank";
  link.rel = "noopener";
});
document.querySelector("#maps-link").href = business.mapsUrl;
document.querySelector("#year").textContent = new Date().getFullYear();

const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const chatStatus = document.querySelector("#chat-status");
const chatPanel = document.querySelector("#chat-panel");
const chatToggle = document.querySelector("#chat-toggle");
const chatClose = document.querySelector("#chat-close");
const chatSubmit = chatForm.querySelector("button[type='submit']");
const apiBaseUrl = window.location.port === "4173" ? "http://localhost:8000" : "";
const chatHistory = [];

function setChatOpen(open) {
  chatPanel.hidden = !open;
  chatToggle.setAttribute("aria-expanded", open);
  if (open) chatInput.focus();
  else chatToggle.focus();
}

function addChatMessage(text, type, contactAdmin = false) {
  const message = document.createElement("div");
  message.className = `chat-message ${type}`;
  message.textContent = text;
  if (contactAdmin) {
    const link = document.createElement("a");
    link.className = "chat-admin-link";
    link.href = createWhatsAppLink("Halo UTC, saya ingin konsultasi mengenai perangkat saya.");
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "Hubungi admin UTC";
    message.append(link);
  }
  chatMessages.append(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setChatTyping(active) {
  const typing = document.querySelector("#chat-typing");
  if (active && !typing) {
    const message = document.createElement("div");
    const dots = document.createElement("span");
    message.className = "chat-message bot chat-typing";
    message.id = "chat-typing";
    message.setAttribute("aria-label", "Asisten UTC sedang mengetik");
    dots.className = "typing-dots";
    dots.setAttribute("aria-hidden", "true");
    for (let index = 0; index < 3; index += 1) dots.append(document.createElement("i"));
    message.append(dots);
    chatMessages.append(message);
  }
  if (!active && typing) typing.remove();
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatToggle.addEventListener("click", () => setChatOpen(chatPanel.hidden));
chatClose.addEventListener("click", () => setChatOpen(false));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !chatPanel.hidden) setChatOpen(false);
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (message.length < 3) return;
  const history = chatHistory.slice(-4);
  addChatMessage(message, "user");
  chatHistory.push({ role: "user", message });
  chatInput.value = "";
  chatInput.disabled = true;
  chatSubmit.disabled = true;
  chatStatus.textContent = "Asisten UTC sedang mengetik.";
  setChatTyping(true);
  try {
    const response = await fetch(`${apiBaseUrl}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, history }) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || "Chatbot belum tersedia.");
    setChatTyping(false);
    addChatMessage(body.answer, "bot", body.contact_admin);
    if (!body.contact_admin) chatHistory.push({ role: "assistant", message: body.answer });
    chatStatus.textContent = body.contact_admin ? "Asisten tidak tersedia. Hubungi admin UTC untuk bantuan." : "Jawaban siap.";
  } catch (error) {
    setChatTyping(false);
    addChatMessage("Maaf, chat sementara tidak dapat terhubung. Silakan hubungi admin UTC.", "bot error", true);
    chatStatus.textContent = "Chatbot belum tersedia.";
  } finally {
    chatInput.disabled = false;
    chatSubmit.disabled = false;
    chatInput.focus();
  }
});

const toggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav-links");
toggle.addEventListener("click", () => {
  const open = navLinks.classList.toggle("open");
  toggle.setAttribute("aria-expanded", open);
  toggle.setAttribute("aria-label", open ? "Tutup menu navigasi" : "Buka menu navigasi");
});
navLinks.addEventListener("click", (event) => {
  if (event.target.matches("a")) { navLinks.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); }
});

const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
  if (entry.isIntersecting) { entry.target.classList.add("visible"); observer.unobserve(entry.target); }
}), { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));
