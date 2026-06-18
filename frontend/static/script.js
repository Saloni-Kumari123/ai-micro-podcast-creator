/* ================= AUTO PROTECT DASHBOARD ================= */
if (window.location.pathname === "/dashboard") {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first!");
        window.location.href = "/login";
    }
}


/* ================= LOGIN ================= */
document.getElementById("loginForm")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok && data.token) {
            localStorage.setItem("token", data.token);  // ✅ Store token

            alert("Login successful!");
            window.location.href = "/dashboard";
        } else {
            alert(data.error || "Invalid credentials");
        }

    } catch (err) {
        alert("Server error. Please try again.");
    }
});


/* ================= REGISTER ================= */
document.getElementById("registerForm")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
        const res = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.ok) {
            alert("Registration successful! Please login.");
            window.location.href = "/login";
        } else {
            alert(data.error || "Registration failed");
        }

    } catch (err) {
        alert("Server error");
    }
});


/* ================= PODCAST GENERATION ================= */
document.getElementById("podcastForm")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const topic = document.getElementById("topic").value.trim();
    const tone = document.getElementById("tone").value;

    const output = document.getElementById("output");

    // 🔐 Check token first
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Session expired. Please login again.");
        window.location.href = "/login";
        return;
    }

    output.innerText = "Generating podcast... ⏳";

    try {
        const res = await fetch("/podcast/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token   // ✅ SEND TOKEN
            },
            body: JSON.stringify({
                topic: topic,
                voice: tone
            })
        });

        // ❌ If token expired or invalid
        if (res.status === 401) {
            alert("Session expired. Please login again.");
            localStorage.removeItem("token");
            window.location.href = "/login";
            return;
        }

        if (!res.ok) {
            const errData = await res.json();
            output.innerText = errData.error || "Error generating podcast";
            return;
        }

        // ✅ Handle audio file
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);

        // 🎧 Download
        const a = document.createElement("a");
        a.href = url;
        a.download = "podcast.mp3";
        a.click();

        output.innerText = "✅ Podcast generated & downloaded successfully!";

    } catch (err) {
        output.innerText = "Server error. Please try again.";
    }
});


/* ================= LOGOUT ================= */
function logout() {
    localStorage.removeItem("token");  // ✅ Clear token
    alert("Logged out successfully");
    window.location.href = "/login";
}