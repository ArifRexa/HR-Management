console.log('js loaded')
let outerHTMLString = `<div id="input-container">
    <input type="text" name="input1" placeholder="Input 1">
    <input type="text" name="input2" placeholder="Input 2">
    <button id="add-button", type="button">Add</button>
</div>
`


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('id_updates_json').outerHTML = outerHTMLString

    const addButton = document.getElementById("add-button");
    const dynamicInputsContainer = document.getElementById("input-container");

    addButton.addEventListener("click", function () {
        // Create new input fields
        const newInput1 = document.createElement("input");
        newInput1.type = "text";
        newInput1.name = "input1";
        newInput1.placeholder = "Input 1";

        const newInput2 = document.createElement("input");
        newInput2.type = "text";
        newInput2.name = "input2";
        newInput2.placeholder = "Input 2";

        // Append new input fields to the container
        dynamicInputsContainer.appendChild(newInput1);
        dynamicInputsContainer.appendChild(newInput2);
    });
});



