async function loginUser() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/ajax/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await res.json();
  const msg = document.getElementById("login-msg");

  if (data.success) {
    window.location.href = "/dashboard";
  } else {
    msg.textContent = data.message;
  }
}

async function registerUser() {
  const username = document.getElementById("username").value;
  const email = document.getElementById("email").value;
  const password1 = document.getElementById("password1").value;
  const password2 = document.getElementById("password2").value;

  const res = await fetch("/ajax/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password1, password2 }),
  });

  const data = await res.json();
  const msg = document.getElementById("register-msg");

  if (data.success) {
    window.location.href = "/login/";
  } else {
    msg.textContent = Object.values(data.errors).join(", ");
  }
}

async function logoutUser() {
  await fetch("/ajax/logout/");
  window.location.href = "/login/";
}

