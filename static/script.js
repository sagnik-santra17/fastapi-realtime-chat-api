const API_URL = "";

let token = localStorage.getItem("token");
let userId = localStorage.getItem("user_id");
let currentSocket = null;
let currentRoomId = null;

// --- DOM Elements ---
const loginContainer = document.getElementById("login-container");
const chatContainer = document.getElementById("chat-container");
const loginSection = document.getElementById("login-section");
const signupSection = document.getElementById("signup-section");
const showSignupBtn = document.getElementById("show-signup");
const showLoginBtn = document.getElementById("show-login");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

// Chat Elements
const roomList = document.getElementById("room-list-items");
const messagesContainer = document.getElementById("messages-container");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const createRoomBtn = document.getElementById("create-room-button");
const logoutBtn = document.getElementById("logout-button");

// Room Action Elements
const roomActions = document.getElementById("room-actions");
const editRoomBtn = document.getElementById("edit-room-btn");
const deleteRoomBtn = document.getElementById("delete-room-btn");

// Profile Modal Elements
const profileModal = document.getElementById("profile-modal");
const profileBtn = document.getElementById("profile-button");
const closeProfileBtn = document.getElementById("close-profile");
const updateProfileForm = document.getElementById("update-profile-form");
const deleteAccountBtn = document.getElementById("delete-account-btn");

// ==========================================
// HELPER: LOADING SPINNER
// ==========================================
function setButtonLoading(button, isLoading, loadingText = "Loading...") {
  if (isLoading) {
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner"></span> ${loadingText}`;
    button.disabled = true;
    button.classList.add("loading");
  } else {
    button.innerHTML = button.dataset.originalText || "Submit";
    button.disabled = false;
    button.classList.remove("loading");
  }
}

// ==========================================
// 1. AUTHENTICATION LOGIC
// ==========================================

showSignupBtn.addEventListener("click", () => {
  loginSection.style.display = "none";
  signupSection.style.display = "block";
});

showLoginBtn.addEventListener("click", () => {
  signupSection.style.display = "none";
  loginSection.style.display = "block";
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = loginForm.querySelector("button");
  setButtonLoading(btn, true, "Logging in...");

  const formData = new URLSearchParams();
  formData.append("username", document.getElementById("username").value);
  formData.append("password", document.getElementById("password").value);

  try {
    const res = await fetch(`${API_URL}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      token = data.access_token;
      localStorage.setItem("token", token);

      const meRes = await fetch(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const meData = await meRes.json();
      userId = meData.user_id;
      localStorage.setItem("user_id", userId);

      loginContainer.style.display = "none";
      chatContainer.style.display = "flex";

      fetchRooms();
      setInterval(fetchRooms, 5000);
    } else {
      alert("Login failed. Check your username and password.");
    }
  } catch (err) {
    alert("Could not connect to the server.");
  } finally {
    setButtonLoading(btn, false);
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = signupForm.querySelector("button");
  setButtonLoading(btn, true, "Creating Account...");

  const username = document.getElementById("signup-username").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const confirm_password = document.getElementById(
    "signup-confirm-password",
  ).value;

  try {
    const res = await fetch(`${API_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        email,
        password,
        confirm_password,
        is_active: true,
      }),
    });

    if (res.ok) {
      alert("Account created successfully! Please log in.");
      signupSection.style.display = "none";
      loginSection.style.display = "block";
    } else {
      const errorData = await res.json();
      alert(
        `Signup failed: ${errorData.detail || "Check console for details"}`,
      );
    }
  } catch (err) {
    alert("Could not connect to the server.");
  } finally {
    setButtonLoading(btn, false);
  }
});

// Logout
logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user_id");
  if (currentSocket) currentSocket.close();

  token = null;
  userId = null;
  currentRoomId = null;

  roomList.innerHTML = "";
  messagesContainer.innerHTML = "";
  document.querySelector(".chat-header h2").textContent = "Select a room";
  roomActions.style.display = "none";

  chatContainer.style.display = "none";
  loginContainer.style.display = "block";
  loginSection.style.display = "block";
  signupSection.style.display = "none";

  // Force reset the login button text
  const loginBtn = loginForm.querySelector("button");
  setButtonLoading(loginBtn, false);
  loginBtn.innerHTML = "Login";
});

// ==========================================
// 2. CHAT & ROOM LOGIC
// ==========================================

async function fetchRooms() {
  try {
    const res = await fetch(`${API_URL}/rooms/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const rooms = await res.json();
      const roomArray = Array.isArray(rooms) ? rooms : rooms.rooms || [];

      if (roomList.children.length !== roomArray.length) {
        roomList.innerHTML = "";
        roomArray.forEach((room) => {
          const li = document.createElement("li");
          li.textContent = room.room_name;
          li.onclick = () =>
            connectToRoom(room.room_id, room.room_name, room.creator_id);
          roomList.appendChild(li);
        });
      }
    }
  } catch (err) {
    console.error("Failed to fetch rooms:", err);
  }
}

async function connectToRoom(roomId, roomName, creatorId) {
  if (currentSocket) currentSocket.close();

  currentRoomId = roomId;
  // Show a loading state so it doesn't look empty while fetching
  messagesContainer.innerHTML =
    "<div style='text-align:center; color:#888; margin-top:20px;'>Loading messages...</div>";
  document.querySelector(".chat-header h2").textContent = roomName;

  // Check ownership for Edit/Delete buttons
  if (parseInt(creatorId) === parseInt(userId)) {
    roomActions.style.display = "flex";
  } else {
    roomActions.style.display = "none";
  }

  try {
    const res = await fetch(`${API_URL}/messages/?room_id=${roomId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    // RACE CONDITION FIX: If user clicks another room while this is loading, ignore this result
    if (currentRoomId !== roomId) return;

    if (res.ok) {
      const pastMessages = await res.json();
      messagesContainer.innerHTML = ""; // Clear loading text

      if (pastMessages.length === 0) {
        messagesContainer.innerHTML =
          "<div style='text-align:center; color:#888; margin-top:20px;'>No messages yet. Say hi!</div>";
      } else {
        pastMessages.forEach((msg) => {
          const isMine = parseInt(msg.sender_id) === parseInt(userId);
          const senderName = isMine ? "You" : `User ${msg.sender_id}`;
          addMessage(
            `${senderName}: ${msg.content}`,
            isMine ? "mine" : "other",
          );
        });
      }
    } else {
      messagesContainer.innerHTML =
        "<div style='text-align:center; color:#ef4444; margin-top:20px;'>Failed to load history.</div>";
    }
  } catch (err) {
    if (currentRoomId === roomId) {
      messagesContainer.innerHTML =
        "<div style='text-align:center; color:#ef4444; margin-top:20px;'>Network error.</div>";
    }
  }

  // Connect WebSocket
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/messages/ws/${roomId}?token=${token}`;
  currentSocket = new WebSocket(wsUrl);

  currentSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const isMine = parseInt(data.user_id) === parseInt(userId);
    const senderName = isMine ? "You" : data.username;

    // If we receive a message, remove the "No messages yet" or "Loading" text
    if (
      messagesContainer.innerHTML.includes("No messages yet") ||
      messagesContainer.innerHTML.includes("Loading messages")
    ) {
      messagesContainer.innerHTML = "";
    }

    addMessage(`${senderName}: ${data.content}`, isMine ? "mine" : "other");
  };
}

messageForm.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!currentSocket || currentSocket.readyState !== WebSocket.OPEN) {
    return alert("Please select a room first!");
  }

  const text = messageInput.value.trim();
  if (!text) return;

  currentSocket.send(JSON.stringify({ content: text }));
  messageInput.value = "";
});

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;
  messagesContainer.appendChild(div);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

createRoomBtn.addEventListener("click", async () => {
  const name = prompt("Enter room name:");
  if (!name) return;

  const payload = { room_name: name, description: "New room" };
  setButtonLoading(createRoomBtn, true, "Creating...");

  try {
    const res = await fetch(`${API_URL}/rooms/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) fetchRooms();
    else alert("Failed to create room.");
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(createRoomBtn, false);
  }
});

// Edit Room Action
editRoomBtn.addEventListener("click", async () => {
  if (!currentRoomId) return;
  const newName = prompt("Enter new room name:");
  if (!newName) return;

  const currentPw = prompt("Enter YOUR ACCOUNT password to confirm:");
  if (!currentPw) return;

  setButtonLoading(editRoomBtn, true, "Saving...");

  try {
    const res = await fetch(`${API_URL}/rooms/${currentRoomId}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ room_name: newName, current_password: currentPw }),
    });

    if (res.ok) {
      alert("Room updated successfully!");
      fetchRooms();
      document.querySelector(".chat-header h2").textContent = newName;
    } else {
      alert("Failed to update room. Check your password.");
    }
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(editRoomBtn, false);
  }
});

// Delete Room Action
deleteRoomBtn.addEventListener("click", async () => {
  if (!currentRoomId) return;

  const currentPw = prompt(
    "Are you sure? Enter YOUR ACCOUNT password to DELETE this room:",
  );
  if (!currentPw) return;

  setButtonLoading(deleteRoomBtn, true, "Deleting...");

  try {
    const res = await fetch(`${API_URL}/rooms/${currentRoomId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ current_password: currentPw }),
    });

    if (res.ok) {
      alert("Room deleted successfully!");
      if (currentSocket) currentSocket.close();
      currentRoomId = null;
      messagesContainer.innerHTML = "";
      document.querySelector(".chat-header h2").textContent = "Select a room";
      roomActions.style.display = "none";
      fetchRooms();
    } else {
      alert("Failed to delete room. Check your password.");
    }
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(deleteRoomBtn, false);
  }
});

// ==========================================
// 3. PROFILE MODAL LOGIC
// ==========================================

profileBtn.addEventListener("click", async () => {
  setButtonLoading(profileBtn, true);
  try {
    const res = await fetch(`${API_URL}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("update-username").value = data.username;
      document.getElementById("update-email").value = data.email;
      document.getElementById("update-password").value = "";
      document.getElementById("current-password").value = "";
      profileModal.classList.add("show");
    }
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(profileBtn, false);
  }
});

closeProfileBtn.addEventListener("click", () => {
  profileModal.classList.remove("show");
});

window.addEventListener("click", (e) => {
  if (e.target === profileModal) profileModal.classList.remove("show");
});

updateProfileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = updateProfileForm.querySelector("button");
  setButtonLoading(btn, true, "Updating...");

  const username = document.getElementById("update-username").value;
  const email = document.getElementById("update-email").value;
  const password = document.getElementById("update-password").value;
  const current_password = document.getElementById("current-password").value;

  const payload = { username, email, current_password };

  if (password.trim() !== "") {
    payload.password = password;
    payload.confirm_password = password;
  }

  try {
    const res = await fetch(`${API_URL}/users/me`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("Profile updated successfully!");
      profileModal.classList.remove("show");
    } else {
      const errorData = await res.json();
      alert(`Failed to update: ${errorData.detail || "Check password"}`);
    }
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(btn, false);
  }
});

deleteAccountBtn.addEventListener("click", async () => {
  const password = prompt(
    "Are you sure? This will permanently delete your account.\nEnter your password to confirm:",
  );
  if (!password) return;

  setButtonLoading(deleteAccountBtn, true, "Deleting...");

  try {
    const res = await fetch(`${API_URL}/users/me`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ password: password }),
    });

    if (res.ok) {
      alert("Account deleted.");
      logoutBtn.click();
    } else {
      alert("Failed to delete account. Check your password.");
    }
  } catch (err) {
    console.error(err);
  } finally {
    setButtonLoading(deleteAccountBtn, false);
  }
});

// ==========================================
// 4. INITIALIZATION
// ==========================================

if (token && userId) {
  loginContainer.style.display = "none";
  chatContainer.style.display = "flex";
  fetchRooms();
  setInterval(fetchRooms, 5000);
}
