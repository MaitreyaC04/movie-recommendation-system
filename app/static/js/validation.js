document.addEventListener("DOMContentLoaded", () => {
    // === Profile Form Validation ===
    const profileForm = document.getElementById("profileForm");
    if (profileForm) {
        const requiredFields = {
            first_name: "First Name",
            last_name: "Last Name",
            dob: "Date of Birth",
            gender: "Gender",
            country: "Country",
            state: "State",
            city: "City/Town"
        };

        // Inline validation for text/select fields
        Object.keys(requiredFields).forEach((fieldId) => {
            const field = document.getElementById(fieldId);
            const errorSpan = document.getElementById(fieldId + "-error");

            field.addEventListener("input", () => {
                if (!field.value.trim()) {
                    errorSpan.textContent = requiredFields[fieldId] + " is required.";
                } else {
                    errorSpan.textContent = "";
                }
            });

            field.addEventListener("change", () => {
                if (!field.value.trim()) {
                    errorSpan.textContent = requiredFields[fieldId] + " is required.";
                } else {
                    errorSpan.textContent = "";
                }
            });
        });

        // Inline validation for streaming platforms
        const platformInputs = document.querySelectorAll('input[name="streaming_platforms"]');
        const platformError = document.getElementById("platform-error");

        platformInputs.forEach(input => {
            input.addEventListener("change", () => {
                const selected = document.querySelectorAll('input[name="streaming_platforms"]:checked');
                if (selected.length === 0) {
                    platformError.textContent = "Select at least one streaming platform.";
                } else {
                    platformError.textContent = "";
                }
            });
        });

        // Final submit validation
        profileForm.addEventListener("submit", (e) => {
            let isValid = true;

            Object.keys(requiredFields).forEach((fieldId) => {
                const field = document.getElementById(fieldId);
                const errorSpan = document.getElementById(fieldId + "-error");
                if (!field.value.trim()) {
                    errorSpan.textContent = requiredFields[fieldId] + " is required.";
                    isValid = false;
                }
            });

            const selectedPlatforms = document.querySelectorAll('input[name="streaming_platforms"]:checked');
            if (selectedPlatforms.length === 0) {
                platformError.textContent = "Select at least one streaming platform.";
                isValid = false;
            }

            if (!isValid) e.preventDefault();
        });
    }

    // === Preferences Form Validation ===
    const preferencesForm = document.getElementById("preferencesForm");
    if (preferencesForm) {
        const groups = [
            { name: "genres", errorId: "genre-error", label: "genre" },
            { name: "languages", errorId: "language-error", label: "language" },
            { name: "actors", errorId: "actor-error", label: "actor" }
        ];

        // Inline validation for each checkbox group
        groups.forEach(group => {
            const checkboxes = document.querySelectorAll(`input[name="${group.name}"]`);
            const errorSpan = document.getElementById(group.errorId);

            checkboxes.forEach(cb => {
                cb.addEventListener("change", () => {
                    const selected = document.querySelectorAll(`input[name="${group.name}"]:checked`);
                    if (selected.length === 0) {
                        errorSpan.textContent = `Select at least one ${group.label}.`;
                    } else {
                        errorSpan.textContent = "";
                    }
                });
            });
        });

        // Final submit validation
        preferencesForm.addEventListener("submit", (e) => {
            let isValid = true;

            groups.forEach(group => {
                const selected = document.querySelectorAll(`input[name="${group.name}"]:checked`);
                const errorSpan = document.getElementById(group.errorId);
                if (selected.length === 0) {
                    errorSpan.textContent = `Select at least one ${group.label}.`;
                    isValid = false;
                }
            });

            if (!isValid) e.preventDefault();
        });
    }
});
