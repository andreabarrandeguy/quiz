document.addEventListener('DOMContentLoaded', (event) => {
    // Accessing the data attributes from the <body> tag
    const body = document.querySelector('body.bodyRoom');
    const name = body.getAttribute('data-name');
    const sender = body.getAttribute('data-sender');
    const receiver = body.getAttribute('data-receiver');
    const completenessSender = body.getAttribute('data-completeness-sender');
    const completenessReceiver = body.getAttribute('data-completeness-receiver');
    const lastUpdateRaw = body.getAttribute('data-last-update');

    const lastUpdate = new Date(lastUpdateRaw).toISOString().split('T')[0];
    const today = new Date().toISOString().split('T')[0];

    // If both have already replied
    if (completenessSender === "True" && completenessReceiver === "True") {
        document.getElementById("waitingContainer").classList.add("hidden");
        document.getElementById("roomLogo").classList.add("hidden");
        document.getElementById("reminderButton").classList.add("hidden");
        document.getElementById("createNewButton").classList.remove("hidden");
        document.getElementById("messageSender").classList.add("hidden");
        document.getElementById("messageReceiver").classList.add("hidden");

        if (name === sender) {
            document.getElementById("carouselSender").classList.remove("hidden");
            document.getElementById("carouselReceiver").classList.add("hidden");
        } else if (name === receiver) {
            document.getElementById("carouselSender").classList.add("hidden");
            document.getElementById("carouselReceiver").classList.remove("hidden");
        }

        // If one of them hasn't replied
    } else if (completenessSender === "False" || completenessReceiver === "False") {
        document.getElementById("roomLogo").classList.remove("hidden");
        document.getElementById("waitingContainer").classList.remove("hidden");
        document.getElementById("reminderButton").classList.remove("hidden");
        document.getElementById("createNewButton").classList.add("hidden");
        document.getElementById("carouselSender").classList.add("hidden");
        document.getElementById("carouselReceiver").classList.add("hidden");

        // Check if the last update was today
        if (lastUpdate === today) {
            const reminderButton = document.getElementById("reminderButton");
            reminderButton.classList.add("disable");
            const reminderWait = document.getElementById("reminderWait");
            if (name === sender) {
                reminderWait.innerHTML = `${receiver} has already been notified today. Come back tomorrow!`;
            } else if (name === receiver) {
                reminderWait.innerHTML = `${sender} has already been notified today. Come back tomorrow!`;
            }
        }

        if (name === sender) {
            document.getElementById("messageSender").classList.add("hidden");
            document.getElementById("messageReceiver").classList.remove("hidden");
        } else if (name === receiver) {
            document.getElementById("messageSender").classList.remove("hidden");
            document.getElementById("messageReceiver").classList.add("hidden");
        }
    }
});

let currentSlideSender = 0;
let currentSlideReceiver = 0;

function moveSlide(direction, carouselId) {
    const carousel = document.querySelector(`#${carouselId} .carousel-slides`);
    const slides = carousel.querySelectorAll('.carousel-slide');
    const totalSlides = slides.length;

    let currentSlide = carouselId === 'carouselSender' ? currentSlideSender : currentSlideReceiver;
    currentSlide = (currentSlide + direction + totalSlides) % totalSlides;

    const offset = -currentSlide * 100;
    carousel.style.transform = `translateX(${offset}%)`;

    if (carouselId === 'carouselSender') {
        currentSlideSender = currentSlide;
    } else {
        currentSlideReceiver = currentSlide;
    }
}
