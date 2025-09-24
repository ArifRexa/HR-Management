document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("id_category");

    // Select the rows of fields you may want to remove
    const displaySizeRow = document.querySelector(".form-row.field-display_size");
    const coreRow = document.querySelector(".form-row.field-core");
    const ramRow = document.querySelector(".form-row.field-ram_size");
    const storageSizeRow = document.querySelector(".form-row.field-storage_size");
    const gpuRow = document.querySelector(".form-row.field-gpu");
    const brandRow = document.querySelector(".form-row.field-brand");
    
    const fields = [
        coreRow, ramRow, storageSizeRow, displaySizeRow, gpuRow
    ];

    function hideAllRowWithout(selected_field){
        // hide All input field Without selected_field input field.
        fields.forEach((field)=>{
            if(field == null) return;
            else if(field != selected_field){
                field.style.display = "none";
            }else{
                field.style.display = "";
            }
        })
    }

    // initially, remove all fields.
    hideAllRowWithout(null);

    function updateFields() {
        const selected = categorySelect.value;
        const selectedText = categorySelect.options[categorySelect.selectedIndex].text;


        if (!selected) return;
        if (selectedText !== "Chair" || selectedText !== "Table"){
            brandRow.style.display = "";
        }
        if (selectedText === "Monitor") {
            hideAllRowWithout(displaySizeRow);
        } else if (selectedText === "Processor") {
           hideAllRowWithout(coreRow);
        } else if (selectedText === "RAM") {
           hideAllRowWithout(ramRow);
        } else if (selectedText === "SSD" || selectedText === "HDD") {
           hideAllRowWithout(storageSizeRow);
        } else if (selectedText === "GPU") {
           hideAllRowWithout(gpuRow);
        }
        else{
            if (selectedText === "Chair" || selectedText === "Table"){
                brandRow.style.display = "none";
            }
            // hide all row if selected category is Headphone or Table or Chair, etc.
            hideAllRowWithout(null);
        }
    }

    if (categorySelect) {
        updateFields(); // on page load
        categorySelect.addEventListener("change", updateFields); // on change
    }
});
