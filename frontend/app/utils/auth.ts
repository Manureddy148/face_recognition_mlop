export async function logoutUser(apiBase: string): Promise<void> {
  try {
    await fetch(`${apiBase}/api/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    // Always clear local session even if backend logout call fails.
  }

  localStorage.removeItem("isLoggedIn");
  localStorage.removeItem("username");
  localStorage.removeItem("userEmail");
  localStorage.removeItem("userId");
  localStorage.removeItem("userType");
  localStorage.removeItem("employeeId");
  localStorage.removeItem("studentId");
}
