const API_URL = "";

let token = localStorage.getItem("token");
let userId = localStorage.getItem("user_id");
let currentSocket = null;
let currentRoomId = null; // Keeps track of which room is open

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
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
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
  loginContainer.style.display = "flex";
  loginSection.style.display = "block";
  signupSection.style.display = "none";
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
          li.onclick = () => connectToRoom(room.room_id, room.room_name);
          roomList.appendChild(li);
        });
      }
    }
  } catch (err) {
    console.error("Failed to fetch rooms:", err);
  }
}

async function connectToRoom(roomId, roomName) {
  if (currentSocket) currentSocket.close();

  currentRoomId = roomId;
  messagesContainer.innerHTML = "";
  document.querySelector(".chat-header h2").textContent = roomName;
  roomActions.style.display = "flex"; // Show edit/delete buttons

  try {
    const res = await fetch(`${API_URL}/messages/?room_id=${roomId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const pastMessages = await res.json();
      pastMessages.forEach((msg) => {
        const isMine = parseInt(msg.sender_id) === parseInt(userId);
        const senderName = isMine ? "You" : `User ${msg.sender_id}`;
        addMessage(`${senderName}: ${msg.content}`, isMine ? "mine" : "other");
      });
    }
  } catch (err) {
    console.log("No history found");
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/messages/ws/${roomId}?token=${token}`;
  currentSocket = new WebSocket(wsUrl);

  currentSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const isMine = parseInt(data.user_id) === parseInt(userId);
    const senderName = isMine ? "You" : data.username;
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
  }
});

// Edit Room Action
editRoomBtn.addEventListener("click", async () => {
  if (!currentRoomId) return;
  const newName = prompt("Enter new room name:");
  if (!newName) return;

  const currentPw = prompt("Enter room password to confirm:");
  if (!currentPw) return;

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
  }
});

// Delete Room Action
deleteRoomBtn.addEventListener("click", async () => {
  if (!currentRoomId) return;
  const currentPw = prompt(
    "Are you sure? Enter room password to DELETE this room:",
  );
  if (!currentPw) return;

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
  }
});

// ==========================================
// 3. PROFILE MODAL LOGIC
// ==========================================

profileBtn.addEventListener("click", async () => {
  // Fetch current profile data to pre-fill the form
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
  }
});

closeProfileBtn.addEventListener("click", () => {
  profileModal.classList.remove("show");
});

// Close modal if clicking outside the box
window.addEventListener("click", (e) => {
  if (e.target === profileModal) profileModal.classList.remove("show");
});

updateProfileForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("update-username").value;
  const email = document.getElementById("update-email").value;
  const password = document.getElementById("update-password").value;
  const current_password = document.getElementById("current-password").value;

  // Build the payload dynamically
  const payload = { username, email, current_password };

  // If they typed a new password, include it and a confirmation
  if (password.trim() !== "") {
    payload.password = password;
    payload.confirm_password = password; // Send same for both to satisfy backend
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
  }
});

deleteAccountBtn.addEventListener("click", async () => {
  const password = prompt(
    "Are you sure? This will permanently delete your account.\nEnter your password to confirm:",
  );
  if (!password) return;

  try {
    const res = await fetch(`${API_URL}/users/me`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ password: password }), // Backend UserDelete schema expects 'password'
    });

    if (res.ok) {
      alert("Account deleted.");
      logoutBtn.click(); // Trigger logout logic
    } else {
      alert("Failed to delete account. Check your password.");
    }
  } catch (err) {
    console.error(err);
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
