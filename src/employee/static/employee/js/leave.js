document.addEventListener("DOMContentLoaded", function () {
    console.log('JavaScript loaded');

    var leaveTypeSelect = document.getElementById('id_leave_type');
    let attachmentInput = document.getElementById('id_leaveattachment_set-0-attachment');

    var saveButton = document.querySelector('input[name="_save"]');
    var saveAndAddAnotherButton = document.querySelector('input[name="_addanother"]');
    var saveAndContinueEditingButton = document.querySelector('input[name="_continue"]');
    
    var deleteButtons = document.querySelectorAll('.delete');
    // console.log(deleteButtons)
    if (deleteButtons){
        deleteButtons[0].style.display = 'none'
    }
        
    
    attachmentInput = document.getElementById('id_leaveattachment_set-0-attachment');
    // Function to enable/disable buttons based on conditions
    function toggleButtons() {      
        if (leaveTypeSelect.value === 'medical') {
            if (attachmentInput != null) {
                if (attachmentInput.files.length > 0) {
                    enableButtons();             
                } 
                else {
            
                    disableButtons();
                }
            }
            else {

                disableButtons();
            }
        } else {
            enableButtons();
        }
    }

    attachmentInput.addEventListener("change", (event) => {
        toggleButtons();
      });
       

    // Function to enable buttons
    function enableButtons() {
        saveButton.disabled = false;
        saveAndAddAnotherButton.disabled = false;
        saveAndContinueEditingButton.disabled = false;
    }

    // Function to disable buttons
    function disableButtons() {
        saveButton.disabled = true;
        saveAndAddAnotherButton.disabled = true;
        saveAndContinueEditingButton.disabled = true;
    }

    // Function to disable all buttons when delete button is clicked
    function handleDeleteButtonClick() {
        disableButtons();
        console.log("clicked delete button")
        attachmentInput = document.getElementById('id_leaveattachment_set-0-attachment');
    }

    // Attach event listeners
    leaveTypeSelect.addEventListener('change', toggleButtons);
    attachmentInput.addEventListener('change', toggleButtons);

    deleteButtons.forEach(function (button) {
        button.addEventListener('click', handleDeleteButtonClick);
    });

    // Initial button state based on leave type
    toggleButtons(); 

    // document.querySelector('.inline-deletelink').addEventListener('load',doLoad)
    document.getElementById('leaveattachment_set-group').addEventListener('load',(e)=>{
        console.log('event loaded!!')
    })
    function doLoad(){
        console.log("image loaded");
    }
    
});

