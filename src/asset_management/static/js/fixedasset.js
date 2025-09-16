// document.addEventListener("DOMContentLoaded", function () {
//     const categorySelect = document.getElementById("id_category");

//     const processorField = document.getElementById("id_processor");
//     const ramField = document.getElementById("id_ram");
//     const displaySizeField = document.getElementById("id_display_size");

//     function toggleReadonly() {
//         const selected = categorySelect.value;
//         console.log('=== selected', selected)
//         if (!selected) return;

//         // Example: adjust category IDs to your database
//         if (selected === "1") {  // Laptop
//             processorField.readOnly = false;
//             ramField.readOnly = false;
//             displaySizeField.readOnly = true;  // make readonly

//         } else if (selected === "2") {  // Monitor
//             processorField.readOnly = true;
//             ramField.readOnly = true;
//             displaySizeField.readOnly = false;

//         } else {
//             // default: all editable
//             processorField.readOnly = false;
//             ramField.readOnly = false;
//             displaySizeField.readOnly = false;
//         }
//     }

//     if (categorySelect) {
//         toggleReadonly();  // initial on page load
//         categorySelect.addEventListener("change", toggleReadonly);  // on change
//     }
// });


document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("id_category");

    // Select the rows of fields you may want to remove
    const displaySizeRow = document.querySelector(".form-row.field-display_size");
    const processorRow = document.querySelector(".form-row.field-processor");
    const ramRow = document.querySelector(".form-row.field-ram");
    const storageRow = document.querySelector(".form-row.field-storage");
    const gpuRow = document.querySelector(".form-row.field-gpu");
    const fields = [
        processorRow, ramRow, storageRow, displaySizeRow, gpuRow, 
    ];
    function hideAllRowWithout(selected_field){
        // hide All input field Without selected_field input field. 
        fields.forEach((field)=>{
            if(field != selected_field){
                field.style.display = "none";
            }else{
                field.style.display = "";
            }
        })
    }

    function updateFields() {
        const selected = categorySelect.value;

        if (!selected) return;
        if (selected === "1") { // "Monitor"
            hideAllRowWithout(displaySizeRow);
        } else if (selected === "2") {  // Processor
           hideAllRowWithout(processorRow);
        } else if (selected === "3") {  // RAM
           hideAllRowWithout(ramRow);
        } else if (selected === "4" || selected === "5") {  // SSD or HDD
           hideAllRowWithout(storageRow);
        } else if (selected === "6") {  // GPU
           hideAllRowWithout(gpuRow);
        }
    }

    if (categorySelect) {
        updateFields(); // on page load
        categorySelect.addEventListener("change", updateFields); // on change
    }
});
