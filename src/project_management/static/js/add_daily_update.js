console.log('js loaded')

let input_container = document.createElement('div')
input_container.id = 'input-container'
let add_btn = document.createElement('button')
add_btn.id = 'add-button'
add_btn.type = 'button'
add_btn.textContent = 'Add'
input_container.appendChild(add_btn)


let input_updates_individuals = []
let input_time_individuals = []
let updates_json_output = []
document.addEventListener("DOMContentLoaded", function () {
    let updates_old = document.getElementsByClassName('form-row field-update')[0]
    let updates_json = document.getElementsByClassName('form-row field-updates_json')[0]
    let updates_json_input_field = document.getElementsByName('updates_json')[0]
    updates_old.style.display = 'None'
    updates_json.appendChild(input_container)
    updates_json_input_field.style.display = 'None'

    const addButton = document.getElementById("add-button");
    const dynamicInputsContainer = document.getElementById("input-container");



    addButton.addEventListener("click", function () {
        document.getElementById('calculate-btn')?.remove()
        // Create new input fields
        const newInput1 = document.createElement("input");
        newInput1.type = "text";
        newInput1.name = "input_update";
        newInput1.placeholder = "Update";
        newInput1.required = true;

        const newInput2 = document.createElement("input");
        newInput2.type = "text";
        newInput2.name = "input_time";
        newInput2.placeholder = "Time";
        newInput2.required = true

        // Append new input fields to the container
        dynamicInputsContainer.appendChild(newInput1);
        dynamicInputsContainer.appendChild(newInput2);

        newInput1.addEventListener('input', function (event){
            // console.log('keystroke : ', event.target.value)
            all_updates = document.getElementsByName('input_update')
            all_times = document.getElementsByName('input_time')
            for (i=0; i<all_updates.length; i++){
                l
                updates_json_output[all_updates[i].value] = all_times[i].value
                console.log('i = '+i+', update: '+all_updates[i].value)
            }

            updates_json_input_field.value = updates_json_output
            console.log('updates: ',updates_json_output)
        })
        newInput2.addEventListener('input', function (event){
            all_updates = document.getElementsByName('input_update')
            all_times = document.getElementsByName('input_time')
            for (i=0; i<all_updates.length; i++){
                updates_json_output[all_updates[i].value] = all_times[i].value
                console.log('i = '+i+', update: '+all_updates[i].value)
            }

            updates_json_input_field.value = updates_json_output.toString()
            console.log('updates: ',updates_json_output.toString())
        })

        let calculate_btn = document.createElement('button')
        calculate_btn.type = "button"
        calculate_btn.id = "calculate-btn"
        calculate_btn.textContent = 'Calculate Hours'


        dynamicInputsContainer.appendChild(calculate_btn)
    });

    // input_updates_individuals = document.getElementsByName('input_name')
    // input_time_individuals = document.getElementsByName('input_time')
    // console.log(input_updates_individuals)
    // console.log(input_time_individuals)
});



