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
        const selectedText = categorySelect.options[categorySelect.selectedIndex].text;

        if (!selected) return;
        if (selectedText === "Monitor") {
            hideAllRowWithout(displaySizeRow);
        } else if (selectedText === "Processor") {
           hideAllRowWithout(processorRow);
        } else if (selectedText === "RAM") {
           hideAllRowWithout(ramRow);
        } else if (selectedText === "SSD" || selectedText === "HDD") {
           hideAllRowWithout(storageRow);
        } else if (selectedText === "GPU") {
           hideAllRowWithout(gpuRow);
        }
        else{
            // hide all row if selected category is Headphone or Table or Chair, etc.
            hideAllRowWithout(null);
        }
    }

    if (categorySelect) {
        updateFields(); // on page load
        categorySelect.addEventListener("change", updateFields); // on change
    }
});
