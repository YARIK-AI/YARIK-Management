function blockButton() {
    document.getElementById("edit-form").addEventListener("submit", function() {
        document.getElementById("save-btn").disabled = true;
    });
}

blockButton();