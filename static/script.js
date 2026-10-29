// The API URL is empty because FastAPI is serving these files
const API_URL = "";

let token = localStorage.getItem("token");
let currentSocket = null;

// --- DOM Elements ---
const loginContainer = document.getElementById("login-container");
const chatContainer = document.getElementById("chat-container");

// Auth Toggle Elements
const loginSection = document.getElementById("login-section");
const signupSection = document.getElementById("signup-section");
const showSignupBtn = document.getElementById("show-signup");
const showLoginBtn = document.getElementById("show-login");

// Forms
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");

// Chat Elements
const roomList = document.getElementById("room-list-items");
const messagesContainer = document.getElementById("messages-container");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const createRoomBtn = document.getElementById("create-room-button");

// ==========================================
// 1. AUTHENTICATION LOGIC (Login & Signup)
// ==========================================

// Toggle to Signup
showSignupBtn.addEventListener("click", () => {
  loginSection.style.display = "none";
  signupSection.style.display = "block";
});

// Toggle to Login
showLoginBtn.addEventListener("click", () => {
  signupSection.style.display = "none";
  loginSection.style.display = "block";
});

// Handle Login Submission
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // Stop page reload

  // FastAPI OAuth2 requires form data, not JSON
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

      // Switch screens
      loginContainer.style.display = "none";
      chatContainer.style.display = "flex";
      fetchRooms();
    } else {
      alert("Login failed. Check your username and password.");
    }
  } catch (err) {
    alert("Could not connect to the server.");
  }
});

// Handle Signup Submission
signupForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // Stop page reload

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
      console.error("Signup Error:", errorData);
      alert(
        `Signup failed: ${errorData.detail || "Check console for details"}`,
      );
    }
  } catch (err) {
    alert("Could not connect to the server.");
  }
});

// ==========================================
// 2. CHAT LOGIC (Rooms & Messages)
// ==========================================

// Fetch and Display Rooms
async function fetchRooms() {
  try {
    const res = await fetch(`${API_URL}/rooms/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const rooms = await res.json();
      roomList.innerHTML = "";

      const roomArray = Array.isArray(rooms) ? rooms : rooms.rooms || [];

      roomArray.forEach((room) => {
        const li = document.createElement("li");
        // UPDATED: Using room_name and room_id to match your database
        li.textContent = room.room_name;
        li.onclick = () => connectToRoom(room.room_id, room.room_name);
        roomList.appendChild(li);
      });
    }
  } catch (err) {
    console.error("Failed to fetch rooms:", err);
  }
}

// Connect to WebSocket
function connectToRoom(roomId, roomName) {
  if (currentSocket) {
    currentSocket.close();
  }

  messagesContainer.innerHTML = "";
  document.querySelector("#chat-window h2").textContent = roomName;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/messages/ws/${roomId}?token=${token}`;

  currentSocket = new WebSocket(wsUrl);

  currentSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    addMessage(data.content, "other");
  };

  currentSocket.onclose = () => {
    console.log(`Disconnected from room ${roomId}`);
  };
}

// Send Message
messageForm.addEventListener("submit", (e) => {
  e.preventDefault();
  if (!currentSocket || currentSocket.readyState !== WebSocket.OPEN) {
    return alert("Please select a room first!");
  }

  const text = messageInput.value.trim();
  if (!text) return;

  currentSocket.send(JSON.stringify({ content: text }));
  addMessage(text, "mine");
  messageInput.value = "";
});

// Helper function to add message bubbles to DOM
function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;
  messagesContainer.appendChild(div);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Create Room
createRoomBtn.addEventListener("click", async () => {
  const name = prompt("Enter room name:");
  if (!name) return;

  const description =
    prompt("Enter room description (optional):") || "New room";
  const password = prompt(
    "Enter room password (optional, leave blank for none):",
  );

  // UPDATED: Using room_name to match your database
  const payload = { room_name: name, description };
  if (password) payload.password = password;

  try {
    const res = await fetch(`${API_URL}/rooms/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      fetchRooms();
    } else {
      alert("Failed to create room.");
    }
  } catch (err) {
    console.error(err);
  }
});

// ==========================================
// 3. INITIALIZATION
// ==========================================

// Check if already logged in on page load
if (token) {
  loginContainer.style.display = "none";
  chatContainer.style.display = "flex";
  fetchRooms();
}
