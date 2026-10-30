const API_URL = "";

let token = localStorage.getItem("token");
let userId = localStorage.getItem("user_id");
let currentSocket = null;

// --- DOM Elements ---
const loginContainer = document.getElementById("login-container");
const chatContainer = document.getElementById("chat-container");
const loginSection = document.getElementById("login-section");
const signupSection = document.getElementById("signup-section");
const showSignupBtn = document.getElementById("show-signup");
const showLoginBtn = document.getElementById("show-login");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const roomList = document.getElementById("room-list-items");
const messagesContainer = document.getElementById("messages-container");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");
const createRoomBtn = document.getElementById("create-room-button");

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

// Handle Login Submission
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

      // Fetch user ID so we know whose messages are ours
      const meRes = await fetch(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const meData = await meRes.json();
      userId = meData.user_id;
      localStorage.setItem("user_id", userId);

      // Switch screens
      loginContainer.style.display = "none";
      chatContainer.style.display = "flex";

      fetchRooms();
      setInterval(fetchRooms, 5000); // Refresh room list every 5 seconds
    } else {
      alert("Login failed. Check your username and password.");
    }
  } catch (err) {
    alert("Could not connect to the server.");
  }
});

// Handle Signup Submission
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

// ==========================================
// 2. CHAT LOGIC
// ==========================================

// Fetch and Display Rooms
async function fetchRooms() {
  try {
    const res = await fetch(`${API_URL}/rooms/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const rooms = await res.json();
      const roomArray = Array.isArray(rooms) ? rooms : rooms.rooms || [];

      // Only redraw if the number of rooms changed (prevents flickering)
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

// Connect to WebSocket and load history
async function connectToRoom(roomId, roomName) {
  if (currentSocket) currentSocket.close();

  messagesContainer.innerHTML = "";
  document.querySelector("#chat-window h2").textContent = roomName;

  // 1. FETCH MESSAGE HISTORY
  try {
    const res = await fetch(`${API_URL}/messages/?room_id=${roomId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const pastMessages = await res.json();
      pastMessages.forEach((msg) => {
        // If the sender_id matches our userId, color it 'mine'
        const isMine = parseInt(msg.sender_id) === parseInt(userId);
        addMessage(msg.content, isMine ? "mine" : "other");
      });
    }
  } catch (err) {
    console.log("No history found");
  }

  // 2. CONNECT WEBSOCKET
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/messages/ws/${roomId}?token=${token}`;

  currentSocket = new WebSocket(wsUrl);

  // 3. LISTEN FOR INCOMING MESSAGES
  currentSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Check if this new message was sent by us or someone else
    const isMine = parseInt(data.user_id) === parseInt(userId);
    addMessage(data.content, isMine ? "mine" : "other");
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

  // Send to server. We DON'T add it to the screen here.
  // The server will broadcast it back, and the listener above will display it.
  currentSocket.send(JSON.stringify({ content: text }));
  messageInput.value = "";
});

// Helper function to add message bubbles
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

if (token && userId) {
  loginContainer.style.display = "none";
  chatContainer.style.display = "flex";
  fetchRooms();
  setInterval(fetchRooms, 5000);
}
