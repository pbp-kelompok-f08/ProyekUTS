async function loginUser() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const msg = document.getElementById("login-msg");
  const btn = document.getElementById("login-btn");
  const spinner = document.getElementById("loading-spinner");
  const btnText = document.getElementById("login-text");

  // Reset pesan
  msg.textContent = "";
  msg.className = "text-sm text-center mt-3";

  // 🚫 Validasi input kosong
  if (!username || !password) {
    msg.textContent = "Username dan password tidak boleh kosong.";
    msg.classList.add("text-red-600");
    return;
  }

  try {
    // ⏳ Loading state
    btn.disabled = true;
    spinner.classList.remove("hidden");
    btnText.textContent = "Logging in...";

    const res = await fetch("/ajax/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();

    // ✅ Kembalikan tombol normal
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.textContent = "Login";

    // 💬 Validasi hasil respon
    if (data.success) {
      msg.textContent = "Login berhasil! Mengalihkan...";
      msg.classList.add("text-green-600");
      setTimeout(() => {
        window.location.href = "/";
      }, 800);
    } else {
      // Kalau password salah / user tidak ditemukan
      if (data.message?.toLowerCase().includes("password")) {
        msg.textContent = "Password salah. Silakan coba lagi.";
      } else if (data.message?.toLowerCase().includes("not found")) {
        msg.textContent = "Username tidak ditemukan.";
      } else {
        msg.textContent = data.message || "Login gagal. Periksa kembali data kamu.";
      }
      msg.classList.add("text-red-600");
    }
  } catch (error) {
    // 🧯 Handle error jaringan
    msg.textContent = "Terjadi kesalahan jaringan. Coba lagi nanti.";
    msg.classList.add("text-red-600");
    btn.disabled = false;
    spinner.classList.add("hidden");
    btnText.textContent = "Login";
  }
}
