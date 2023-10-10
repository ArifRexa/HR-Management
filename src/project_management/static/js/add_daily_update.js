console.log('js loaded')

let input_container = document.createElement('div')
input_container.id = 'input-container'
let add_btn = document.createElement('button')
add_btn.id = 'add-button'
add_btn.type = 'button'
add_btn.textContent = 'Add'
input_container.appendChild(add_btn)
input_container.appendChild(document.createElement('br'))


let input_updates_individuals = []
let input_time_individuals = []
let updates_json_output = []
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('id_hours').readonly = true
    let updates_old = document.getElementsByClassName('form-row field-update')[0]
    let updates_json = document.getElementsByClassName('form-row field-updates_json')[0]
    let updates_json_input_field = document.getElementsByName('updates_json')[0]
    // updates_old.style.display = 'None'
    updates_json.appendChild(input_container)
    updates_json_input_field.style.display = 'None'
    updates_json_input_field.innerText = 'hello'

    const addButton = document.getElementById("add-button");
    const dynamicInputsContainer = document.getElementById("input-container");



    addButton.addEventListener("click", function () {
        document.getElementById('calculate-btn')?.remove()
        // Create new input fields
        const update_text = document.createElement("input");
        update_text.type = "text";
        update_text.name = "input_update";
        update_text.placeholder = "Update";
        update_text.required = true;

        const update_hour = document.createElement("input");
        update_hour.type = "number";
        update_hour.name = "input_time";
        update_hour.placeholder = "Time";
        update_hour.required = true

        // Append new input fields to the container
        dynamicInputsContainer.appendChild(update_text);
        dynamicInputsContainer.appendChild(update_hour);
        dynamicInputsContainer.appendChild(document.createElement('br'))

        // let calculate_btn = document.createElement('button')
        // calculate_btn.type = "button"
        // calculate_btn.id = "calculate-btn"
        // calculate_btn.textContent = 'Calculate Hours'
        //
        //
        // dynamicInputsContainer.appendChild(calculate_btn)


        update_hour.addEventListener('keyup', function (event){
        // calculate_btn.addEventListener('click', function (event){
            // console.log('keystroke : ', event.target.value)
            all_updates = document.getElementsByName('input_update')
            all_times = document.getElementsByName('input_time')
            // let json__ = {}
            let updates = []
            for (i=0; i<all_updates.length; i++){
                // console.log(all_updates[i].value.toString())
                // console.log(all_times[i].value.toString())
                let individual_update = [all_updates[i].value, all_times[i].value]
                updates.push(individual_update)
            }
            updates_json_input_field.innerText = JSON.stringify(updates)
            // console.log('updates: ', JSON.stringify(updates))
            let total_hour = 0.0
            all_times.forEach((time_of_one)=>{
                total_hour += time_of_one.value?parseFloat(time_of_one.value):0
                console.log(time_of_one.value)
            })
            document.getElementById('id_hours').value = total_hour

        })


    });
});



