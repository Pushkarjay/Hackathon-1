document.addEventListener("DOMContentLoaded", () => {
    const processButton = document.getElementById("process-button");
    const uploadForm = document.getElementById("upload-form");

    processButton.addEventListener("click", () => {
        processButton.textContent = "Processing...";
        processButton.disabled = true;
        processButton.style.opacity = "0.7";
    });

    uploadForm.addEventListener("submit", () => {
        setTimeout(() => {
            processButton.textContent = "Process";
            processButton.disabled = false;
            processButton.style.opacity = "1";
        }, 3000); // Simulate a delay for demonstration
    });
});
