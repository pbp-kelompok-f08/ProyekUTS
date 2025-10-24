async function deleteUser(userId) {
  const res = await fetch(`/ajax/delete-user/${userId}/`);
  const data = await res.json();

  if (data.success) {
    document.getElementById(`user-${userId}`).remove();
  } else {
    alert("Gagal menghapus user!");
  }
}
