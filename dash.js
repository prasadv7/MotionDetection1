const firebaseConfig = {
  apiKey: "AIzaSyAI0HKDbs8LmelfuSBt0zS7TINuI_x8Sew",
  authDomain: "motiondetection-371f1.firebaseapp.com",
  databaseURL: "https://motiondetection-371f1-default-rtdb.firebaseio.com",
  projectId: "motiondetection-371f1",
  storageBucket: "motiondetection-371f1.appspot.com",
  messagingSenderId: "139872582458",
  appId: "1:139872582458:web:3c9fb044d761170c9e6e03",
  measurementId: "G-9LGSLNVL3T"
};
let studentList = document.getElementById('studentList');
let allStudents = [];
        firebase.initializeApp(firebaseConfig);

        // Reference to Firebase Firestore
        const firestore = firebase.firestore();

        // Reference to Firebase Storage
        const storage = firebase.storage();

        // Reference to the students collection
        const studentsRef = firestore.collection('students');

        // Function to retrieve and display student data
        // Function to retrieve and display student data
function displayStudentData(studentId) {
    const studentDocRef = studentsRef.doc(studentId);

    studentDocRef.get().then((doc) => {
        const studentDetails = document.getElementById("studentDetails");
        const screenshotContainer = document.getElementById("screenshotContainer");
        const logFileLink = document.getElementById("logFileLink");
        const studentVideo = document.getElementById("studentVideo");

        if (doc.exists) {
            const studentData = doc.data();
            const studentName = document.getElementById("studentName");
            studentName.textContent = studentData.name;

            // Clear existing screenshots
            while (screenshotContainer.firstChild) {
                screenshotContainer.removeChild(screenshotContainer.firstChild);
            }
            if (studentData.video_url) {
                console.log("Video URL:", studentData.video_url);

                studentVideo.src = studentData.video_url;
                studentVideo.style.display = 'block'; // Show the video player
            } else {
                studentVideo.style.display = 'none'; // Hide the video player if no video URL
            }


            if (studentData.screenshot_urls && studentData.screenshot_urls.length > 0) {
                studentData.screenshot_urls.forEach(screenshotUrl => {
                    const img = document.createElement('img');
                    img.src = screenshotUrl;
                    img.classList.add('screenshot');
                    screenshotContainer.appendChild(img);
                });
            } else {
                const noDataMessage = document.createElement('p');
                noDataMessage.textContent = "No captured data available for this student.";
                screenshotContainer.appendChild(noDataMessage);
            }

            if (studentData.log_url) {
                const viewLogButton = document.createElement('button');
                viewLogButton.textContent = "View Log";
                viewLogButton.onclick = function () {
                    // Fetch log content
                    fetch(studentData.log_url)
                        .then(response => response.text())
                        .then(data => {
                            const logContent = document.createElement('pre');
                            logContent.textContent = data;
                            logContent.classList.add('logContent');
                            studentDetails.appendChild(logContent);
                        })
                        .catch(error => {
                            console.error("Error fetching log file:", error);
                        });

                    // Hide the log file link and the View Log button after it's clicked
                    viewLogButton.style.display = "none";
                    logFileLink.style.display = "none";
                };

                studentDetails.appendChild(viewLogButton);

                // Hide the log file link initially
                logFileLink.style.display = "none";
            }

            // Rest of your existing code to display video, log, and more
        } else {
            // Show message if the student document does not exist
            const noDataMessage = document.createElement('p');
            noDataMessage.textContent = "No captured data available for this student.";
            studentDetails.appendChild(noDataMessage);
        }
    }).catch((error) => {
        console.error("Error retrieving student data:", error);
    });
}

function displayStudentNames(students) {
    const studentList = document.getElementById('studentList');
    studentList.innerHTML = '';

    if (students.length === 0) {
        const noStudentMessage = document.createElement('li');
        noStudentMessage.textContent = 'No such student found';
        studentList.appendChild(noStudentMessage);
    } else {
        students.forEach((studentData) => {
            const studentItem = document.createElement('li');
            studentItem.style.display = 'flex';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `student_${studentData.id}`;
            checkbox.value = studentData.id;

            const label = document.createElement('label');
            label.htmlFor = `student_${studentData.id}`;
            label.textContent = studentData.name;
            label.style.cursor = 'pointer';
            label.style.marginLeft = '10px';

            label.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                displayStudentData(studentData.id);
            });

            studentItem.appendChild(checkbox);
            studentItem.appendChild(label);
            studentList.appendChild(studentItem);
        });

        // Create and add the delete button
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete Selected Students';
        deleteButton.onclick = deleteSelectedStudents; // Call the delete function on button click
        studentList.appendChild(deleteButton);
    }
}
const deleteButton = document.getElementById('deleteButton');

// Function to handle the deletion confirmation and process
function deleteSelectedStudents() {
    const studentCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const studentIds = Array.from(studentCheckboxes).map(checkbox => checkbox.value);

    if (studentIds.length > 0) {
        if (confirm("Are you sure you want to delete the selected students?")) {
            studentIds.forEach(studentId => {
                deleteStudent(studentId);
            });
        } else {
            console.log("Deletion canceled");
        }
    } else {
        alert("Please select at least one student to delete.");
    }
}

// Function to delete a single student
function deleteStudent(studentId) {
    const studentDocRef = studentsRef.doc(studentId);
    studentDocRef
        .delete()
        .then(() => {
            console.log('Document successfully deleted!');
            updateStudentListAfterDeletion(studentId);
        })
        .catch((error) => {
            console.error('Error removing document: ', error);
        });
}

// Function to update the student list after deletion
function updateStudentListAfterDeletion(deletedStudentId) {
    allStudents = allStudents.filter(student => student.id !== deletedStudentId);
    displayStudentNames(allStudents);
}

// Add an event listener to the delete button
deleteButton.addEventListener('click', deleteSelectedStudents);
function showHideDeleteButton() {
    const studentCheckboxes = document.querySelectorAll('input[type="checkbox"]');
    const deleteButton = document.getElementById('deleteButton');

    let atLeastOneSelected = false;
    studentCheckboxes.forEach(checkbox => {
        if (checkbox.checked) {
            atLeastOneSelected = true;
        }
    });

    if (atLeastOneSelected) {
        deleteButton.style.display = 'block';
    } else {
        deleteButton.style.display = 'none';
    }
}

// Add an event listener to call showHideDeleteButton function when checkboxes are clicked
document.addEventListener('change', function(e) {
    if (e.target && e.target.type === 'checkbox') {
        showHideDeleteButton();
    }
});
function filterStudents(searchValue) {
  const filteredStudents = allStudents.filter(student => student.name.toLowerCase().includes(searchValue.toLowerCase()));
  displayStudentNames(filteredStudents);
}

function setupSearchListener() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', () => {
    const searchValue = searchInput.value.trim();
    if (searchValue !== '') {
      filterStudents(searchValue);
    } else {
      displayStudentNames(allStudents);
    }
  });
}

studentsRef.get().then((querySnapshot) => {
  querySnapshot.forEach((doc) => {
    const studentData = doc.data();
    allStudents.push({ id: doc.id, name: studentData.name });
  });
  displayStudentNames(allStudents);
  setupSearchListener();
});

        // script.js
// Add this JavaScript to your dash.js file
function switchTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const tabButtons = document.querySelectorAll('.tab-button');

    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    tabButtons.forEach(button => {
        button.classList.remove('active');
    });

    const selectedTab = document.getElementById(tabName + 'Tab');
    const selectedButton = document.getElementById(tabName + 'TabButton');

    selectedTab.classList.add('active');
    selectedButton.classList.add('active');
}

function displayScreenshots() {
    const screenshotContainer = document.getElementById("screenshotContainer");
    // Replace with code to fetch and display screenshots

}
