document.addEventListener("DOMContentLoaded", (event) => {
    // Access data attributes from the body element
    const bodyElement = document.body;
    const name = bodyElement.getAttribute("data-name");
    const sender = bodyElement.getAttribute("data-sender");
    const receiver = bodyElement.getAttribute("data-receiver");

    // Show personalized form for sender
    if (name === sender) {
        document.getElementById("answersSender").classList.remove("hidden");
        document.getElementById("answersReceiver").classList.add("hidden");
    } else if (name === receiver) {
        document.getElementById("answersSender").classList.add("hidden");
        document.getElementById("answersReceiver").classList.remove("hidden");
    }

    function checkInputs() {
        const inputsSender = document.querySelectorAll('.answerInputSender');
        const inputsReceiver = document.querySelectorAll('.answerInputReceiver');
        const buttonSender = document.getElementById('submitButtonSender');
        const buttonReceiver = document.getElementById('submitButtonReceiver');

        if (name === sender) {
            const allFilledSender = Array.from(inputsSender).every(input => input.value.trim() !== '');
            if (allFilledSender) {
                buttonSender.classList.add('done');
            } else {
                buttonSender.classList.remove('done');
            }
        } else if (name === receiver) {
            const allFilledReceiver = Array.from(inputsReceiver).every(input => input.value.trim() !== '');
            if (allFilledReceiver) {
                buttonReceiver.classList.add('done');
            } else {
                buttonReceiver.classList.remove('done');
            }
        }
    }

    document.querySelectorAll('.answerInputSender, .answerInputReceiver').forEach(input => {
        input.addEventListener('input', checkInputs);
    });

    // Initial check in case the inputs are pre-filled
    checkInputs();
});