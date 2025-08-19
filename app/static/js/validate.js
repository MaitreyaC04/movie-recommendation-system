// === Regex patterns ===
const emailRegex = /^[a-zA-Z0-9._%+-]+@(gmail|yahoo|outlook)\.com$/;
const phoneRegex = /^[1-9][0-9]{9}$/;
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

// === Signup Validation ===
function validateSignup() {
    return (
        validateEmail() &
        validatePhone() &
        validatePassword() &
        validateConfirmPassword()
    );
}

// Email validation
function validateEmail() {
    let email = document.getElementById("email").value.trim().toLowerCase();
    let msg = document.getElementById("email_error");

    if (!emailRegex.test(email)) {
        msg.textContent = "❌ Must be Gmail, Yahoo, or Outlook only.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Valid email.";
    msg.style.color = "green";
    return true;
}

// Phone validation
function validatePhone() {
    let phone = document.getElementById("phone").value.trim();
    let msg = document.getElementById("phone_error");

    if (!phoneRegex.test(phone)) {
        msg.textContent = "❌ Must be 10 digits, not starting with 0.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Valid phone number.";
    msg.style.color = "green";
    return true;
}

// Password validation
function validatePassword() {
    let password = document.getElementById("password").value.trim();
    let msg = document.getElementById("password_error");

    if (!passwordRegex.test(password)) {
        msg.textContent = "❌ At least 8 characters, 1 uppercase, 1 lowercase, 1 number.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Strong password.";
    msg.style.color = "green";
    return true;
}

// Confirm password validation
function validateConfirmPassword() {
    let password = document.getElementById("password").value.trim();
    let confirmPassword = document.getElementById("confirm_password").value.trim();
    let msg = document.getElementById("confirm_error");

    if (password !== confirmPassword || confirmPassword === "") {
        msg.textContent = "❌ Passwords do not match.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Passwords match.";
    msg.style.color = "green";
    return true;
}

// === Login Validation ===
function validateLogin() {
    return validateIdentifier() & validateLoginPassword();
}

// Identifier (email/phone)
function validateIdentifier() {
    let identifier = document.getElementById("identifier").value.trim();
    let msg = document.getElementById("identifier_error");

    if (identifier.length < 3) {
        msg.textContent = "❌ Enter a valid email or phone.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Looks good.";
    msg.style.color = "green";
    return true;
}

// Password check
function validateLoginPassword() {
    let password = document.getElementById("login_password").value.trim();
    let msg = document.getElementById("login_password_error");

    if (password.length < 8) {
        msg.textContent = "❌ Password must be at least 8 characters.";
        msg.style.color = "red";
        return false;
    }
    msg.textContent = "✅ Valid password length.";
    msg.style.color = "green";
    return true;
}

// === Attach Real-time Event Listeners ===
window.onload = function() {
    if (document.getElementById("email")) {
        document.getElementById("email").addEventListener("input", validateEmail);
        document.getElementById("phone").addEventListener("input", validatePhone);
        document.getElementById("password").addEventListener("input", validatePassword);
        document.getElementById("confirm_password").addEventListener("input", validateConfirmPassword);
    }
    if (document.getElementById("identifier")) {
        document.getElementById("identifier").addEventListener("input", validateIdentifier);
        document.getElementById("login_password").addEventListener("input", validateLoginPassword);
    }
};
