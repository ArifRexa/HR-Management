// static/js/candidate_actions.js

// Define getCsrfToken function first
function getCsrfToken() {
    let csrfToken = null;

    // First try to get the token from the cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
            break;
        }
    }

    // If not found in cookie, try to get it from the form
    if (!csrfToken) {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            csrfToken = tokenElement.value;
        }
    }

    if (!csrfToken) {
        throw new Error('CSRF token not found');
    }

    return csrfToken;
}

// // Initialize when document is ready
// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize datetime picker if you're using it
//     if (typeof flatpickr !== 'undefined') {
//         flatpickr(".schedule-datetime", {
//             enableTime: true,
//             dateFormat: "Y-m-d H:i",
//             onChange: function(selectedDates, dateStr, instance) {
//                 const candidateId = instance.element.closest('.candidate-actions').dataset.candidateId;
//                 updateSchedule(candidateId, dateStr);
//             }
//         });
//     }
// });
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flatpickr with custom config
    if (typeof flatpickr !== 'undefined') {
        flatpickr(".schedule-datetime", {
            enableTime: true,
            dateFormat: "Y-m-d h:i",
            minDate: "today",
            time_24hr: false,
            minuteIncrement: 15,
            defaultHour: 9,
            onChange: function(selectedDates, dateStr, instance) {
                const candidateId = instance.element.closest('.candidate-actions').dataset.candidateId;
                updateSchedule(candidateId, dateStr);
            },
            onOpen: function(selectedDates, dateStr, instance) {
                instance.element.parentElement.classList.add('active');
            },
            onClose: function(selectedDates, dateStr, instance) {
                instance.element.parentElement.classList.remove('active');
            }
        });
    }
});
async function makeRequest(url, data) {
    const actionItem = document.querySelector(`[data-candidate-id="${data.candidateId}"]`);
    const messageDiv = actionItem?.querySelector('.message') || document.createElement('div');

    try {
        if (actionItem) actionItem.classList.add('loading');
        messageDiv.textContent = 'Updating...';

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        if (responseData.status === 'success') {
            messageDiv.textContent = 'Updated successfully';
            messageDiv.className = 'message success-message';
            setTimeout(() => {
                messageDiv.textContent = '';
            }, 2000);
        }
        return responseData;
    } catch (error) {
        console.error('Error:', error);
        messageDiv.textContent = 'Failed to update';
        messageDiv.className = 'message error-message';
        throw error;
    } finally {
        if (actionItem) actionItem.classList.remove('loading');
    }
}

async function updateShortlist(candidateId, value) {
    await makeRequest(
        `/api/candidate/${candidateId}/shortlist/`,  // Remove 'action' from URL
        {
            is_shortlisted: value,
            candidateId: candidateId
        }
    );
}

async function updateCall(candidateId, value) {
    await makeRequest(
        `/api/candidate/${candidateId}/call/`,  // Remove 'action' from URL
        {
            is_called: value,
            candidateId: candidateId
        }
    );
}

// async function updateSchedule(candidateId, value) {
//     await makeRequest(
//         `/api/candidate/${candidateId}/schedule/`,  // Remove 'action' from URL
//         {
//             schedule_datetime: value,
//             candidateId: candidateId
//         }
//     );
// }
let scheduleTimeout = null;  // Store the timeout globally

async function updateSchedule(candidateId, value) {
    const scheduleContainer = document.querySelector(`[data-candidate-id="${candidateId}"] .schedule-input-wrapper`);
    const cancelButton = scheduleContainer.querySelector('.cancel-schedule-btn');

    // Clear any existing timeout to prevent duplicate API calls
    if (scheduleTimeout) {
        clearTimeout(scheduleTimeout);
    }

    // Set a timeout to delay the API call by 10 seconds
    scheduleTimeout = setTimeout(async () => {
        const response = await makeRequest(
            `/api/candidate/${candidateId}/schedule/`,
            {
                schedule_datetime: value,
                candidateId: candidateId
            }
        );

        // If the schedule is successfully updated, add the cancel button if not present
        if (response.status === 'success') {
            if (!cancelButton) {
                const newCancelButton = document.createElement('button');
                newCancelButton.textContent = 'Cancel';
                newCancelButton.type = 'button';
                newCancelButton.className = 'cancel-schedule-btn';
                newCancelButton.onclick = function () {
                    cancelSchedule(candidateId);
                };
                scheduleContainer.appendChild(newCancelButton);
            }
        }
    }, 10000);  // Delay of 10 seconds
}

async function cancelSchedule(candidateId) {
    const inputField = document.querySelector(`[data-candidate-id="${candidateId}"] .schedule-datetime`);
    inputField.value = '';  // Clear the input field

    // Clear the timeout to prevent the delayed API call
    if (scheduleTimeout) {
        clearTimeout(scheduleTimeout);
        scheduleTimeout = null;  // Reset timeout reference
    }

    // Optionally send request to backend to clear the schedule immediately
    await makeRequest(
        `/api/candidate/${candidateId}/schedule/`,  // API endpoint
        {
            schedule_datetime: null,  // Reset the schedule in the database
            candidateId: candidateId
        }
    );
}



async function updateFeedback(candidateId, value) {
    await makeRequest(
        `/api/candidate/${candidateId}/feedback/`,  // Remove 'action' from URL
        {
            feedback: value,
            candidateId: candidateId
        }
    );
}

async function updateStatus(candidateId, value) {
    await makeRequest(
        `/api/candidate/${candidateId}/status/`,  // Remove 'action' from URL
        {
            application_status: value,
            candidateId: candidateId
        }
    );
}

