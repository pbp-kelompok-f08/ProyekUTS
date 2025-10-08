function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const colors = {
    success: "bg-green-600 text-white",
    error: "bg-red-600 text-white",
    info: "bg-blue-600 text-white",
  };

  const toast = document.createElement("div");
  toast.className = `rounded-lg shadow-lg px-4 py-3 ${colors[type]} animate-slide-in-right`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-x-5");
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}

const style = document.createElement("style");
style.innerHTML = `
@keyframes slide-in-right {
  0% { transform: translateX(100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}
.animate-slide-in-right {
  animation: slide-in-right 0.4s ease-out forwards;
}
`;
document.head.appendChild(style);
