document.addEventListener("DOMContentLoaded", function () {
    var indexCreateButton = document.getElementById("indexCreateButton");
    var circleAnimation = document.getElementById("circleAnimation");
    var redirectUrl = indexCreateButton.getAttribute("data-redirect-url"); // Get the URL from the data attribute

    indexCreateButton.addEventListener("click", function () {
        circleAnimation.classList.add("animate");
        setTimeout(function () {
            window.location.href = redirectUrl;
        }, 300); // Match the duration of the CSS animation
    });
});
