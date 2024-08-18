document.addEventListener("DOMContentLoaded", () => {
    const addQuestionButton = document.getElementById("addQuestionButton");
    const questionInput = document.querySelector("[name='question']");
    const hasQuestionsElement = document.getElementById("has_questions");
    const inputQuestions = document.getElementById("inputQuestions");
    const createRoomButton = document.getElementById("createRoom");
    const randomButton = document.getElementById("randomButton");

    const receiverInput = document.getElementById("id_other_person_name");
    const receiverShow = document.getElementById("receiverShow");
    const receiverShow2 = document.getElementById("receiverShow2");

    // Retrieve the saved value from local storage and set it to receiverShow and receiverShow2
    const savedReceiverName = localStorage.getItem("receiverName");
    if (savedReceiverName) {
        receiverShow.innerHTML = savedReceiverName;
        receiverShow2.innerHTML = savedReceiverName;
        receiverInput.value = savedReceiverName;  // If you want the input field to also reflect the saved value
    }

    // Listen for keyup events on the receiverInput field
    receiverInput.addEventListener("keyup", function () {
        const currentReceiverName = receiverInput.value;
        receiverShow.innerHTML = currentReceiverName;
        receiverShow2.innerHTML = currentReceiverName;

        // Save the current value to local storage
        localStorage.setItem("receiverName", currentReceiverName);
    });

    // Define the list of random questions
    const questionsList = [
        "What is your favorite book?",
        "If you could visit any place in the world, where would you go?",
        "What is the most memorable trip you've ever taken?",
        "What hobby would you like to pick up if you had more time?",
        "Who is someone you admire and why?",
        "What is a skill you'd like to learn and why?",
        "What is your favorite movie and why?",
        "If you could have dinner with any historical figure, who would it be?",
        "What is your go-to comfort food?",
        "What was the last book you read and enjoyed?",
    ];

    // Function to update the display based on question count
    function updateQuestionCount() {
        const hasQuestions = parseInt(hasQuestionsElement.value, 10);
        if (hasQuestions > 4) {
            inputQuestions.style.display = "none";
            createRoomButton.classList.add("done");
        } else {
            inputQuestions.style.display = "flex";
            createRoomButton.classList.remove("done");
        }
    }

    // Initial check on page load
    updateQuestionCount();

    // Handle question addition
    addQuestionButton.addEventListener("click", function (event) {
        const questionText = questionInput.value.trim();
        if (questionText === "") {
            alert("Please enter a question before adding");
            event.preventDefault();
            return;
        }

        // Increment the hidden field value
        let hasQuestions = parseInt(hasQuestionsElement.value, 10);
        hasQuestions++;
        hasQuestionsElement.value = hasQuestions;

        updateQuestionCount();
    });

    // Handle random question generation
    randomButton.addEventListener("click", function () {
        const randomIndex = Math.floor(Math.random() * questionsList.length);
        const randomQuestion = questionsList[randomIndex];
        questionInput.value = randomQuestion;
    });

    // Handle form submission
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        const hasQuestions = parseInt(hasQuestionsElement.value, 10);
        const userName = document.getElementById("id_user_name").value.trim().toLowerCase();
        const otherPersonName = document.getElementById("id_other_person_name").value.trim().toLowerCase();
        if (userName === otherPersonName) {
            alert("Your name and the receiver's name can't be the same, sorry for the inconvenience!");
            event.preventDefault(); // Prevent form submission
        }
        if (hasQuestions < 1) {
            alert("You must at least add one question to create a room");
            event.preventDefault(); // Prevent form submission
            return;
        }
    });
});