console.log('js loaded')

let input_container = document.createElement('div')
input_container.id = 'input-container'
let add_btn = document.createElement('button')
add_btn.id = 'add-button'
add_btn.type = 'button'
add_btn.textContent = 'Add'
// input_container.appendChild(document.createElement('br'))
// input_container.appendChild(document.createElement('br'))
input_container.appendChild(add_btn)
// input_container.appendChild(document.createElement('br'))



let input_updates_individuals = []
let input_time_individuals = []
let updates_json_output = []
let dynamicInputsContainer
let updates_json_input_field
let count = 1

document.addEventListener("DOMContentLoaded", function () {
    let formType = window.location.pathname.split('/')
    formType = formType[formType.length - 2]
    console.log(formType)

    document.getElementsByClassName('form-row field-updates_json')[0].getElementsByTagName('label')[0].innerText = 'Updates:'

    // document.getElementById('id_hours').readonly = true
    if (document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0] != null){
        console.log('cannot edit updates')
        let updates = document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0].innerText
        updates = JSON.parse(updates)
        let html_updates = "<ol name='updates_json'>"
        for (i=1; i<=updates.length; i++){
            html_updates += `<li> ${updates[i-1][0]} - ${updates[i-1][1]}H. </li>`
        }
        html_updates += "</ol>"
        document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0].innerHTML = html_updates
        console.log(updates)

        // ref-here
        // document.getElementById('id_hours') && (document.getElementById('id_hours').style.display = 'None')
        // let hours_div = document.getElementsByClassName('form-row field-hours')[0]
        // let updates_old = document.getElementsByClassName('form-row field-update')[0]
        // let updates_json = document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0]
        // updates_json.innerText = ''
        // updates_json.style.marginLeft = 0
        // // updates_json_input_field = document.getElementsByName('updates_json')[0]
        // // let updates_json_input_field = document.getElementsByName('updates_json')[0]
        // // updates_old.style.display = 'None'
        //
        // updates_json.appendChild(input_container)
        // // updates_json.style.display = 'none'
        // // console.log(updates_json_input_field.innerText)
        //
        // const addButton = document.getElementById("add-button");
        // // const dynamicInputsContainer = document.getElementById("input-container");
        // dynamicInputsContainer = document.getElementById("input-container");
        //
        // let show_hour = document.createElement('span')
        // show_hour.id = 'show-hour'
        // show_hour.textContent = document.getElementById('id_hours').value.toString()
        // hours_div.appendChild(show_hour)
        //
        // // let existing_updates = JSON.parse(updates_json_input_field.innerText)
        // // console.log(existing_updates)
        // updates.forEach((line_updates) => {
        //     add_update_element(line_updates)
        //
        // })

    }
    else {

        document.getElementById('id_hours') && (document.getElementById('id_hours').style.display = 'None')
        let hours_div = document.getElementsByClassName('form-row field-hours')[0]
        let updates_old = document.getElementsByClassName('form-row field-update')[0]
        let updates_json = document.getElementsByClassName('form-row field-updates_json')[0]
        updates_json_input_field = document.getElementsByName('updates_json')[0]
        // let updates_json_input_field = document.getElementsByName('updates_json')[0]
        // updates_old.style.display = 'None'

        updates_json.appendChild(input_container)
        updates_json_input_field.style.display = 'none'

        const addButton = document.getElementById("add-button");
        // const dynamicInputsContainer = document.getElementById("input-container");
        dynamicInputsContainer = document.getElementById("input-container");

        if (formType == 'add') {
            document.getElementsByClassName('form-row field-update')[0].style.display = 'None'
            let show_hour = document.createElement('span')
            show_hour.id = 'show-hour'
            show_hour.textContent = '0.0'
            hours_div.appendChild(show_hour)

            updates_json_input_field.innerText = 'hello'

        }
        else if (formType == 'change') {
            let show_hour = document.createElement('span')
            show_hour.id = 'show-hour'
            show_hour.textContent = document.getElementById('id_hours').value.toString()
            hours_div.appendChild(show_hour)

            let existing_updates = JSON.parse(updates_json_input_field.innerText)
            console.log(existing_updates)
            existing_updates.forEach((line_updates) => {
                add_update_element(line_updates)

            })

        }


        addButton.addEventListener("click", function () {
            add_update_element()
        });
    }
});



function add_update_element(existing_values=null){
    // Create new input fields
    // const update_text = document.createElement("input");
    const cs_form_group_div = document.createElement('div')
    cs_form_group_div.className = "cs-form-group"
    cs_form_group_div.id = `cs-form-group-${count}`

    const update_text = document.createElement("textarea");
    update_text.type = "text";
    update_text.name = "input_update";
    update_text.id = `input_update-${count}`;
    update_text.className = "cs-form-control-text"
    update_text.placeholder = "Update";
    update_text.required = true;

    const update_hour = document.createElement("input");
    update_hour.type = "number";
    update_hour.name = "input_time";
    update_hour.id = `input_time-${count}`;
    update_hour.className = "cs-form-control"
    update_hour.placeholder = "Time";
    update_hour.required = true

    const remove_update_btn = document.createElement('button')
    remove_update_btn.type = "button"
    remove_update_btn.id = `remove-button-${count}`
    remove_update_btn.textContent = "Remove"
    remove_update_btn.className = 'remove-update-btn'

    if (existing_values != null){
        update_text.value = existing_values[0]
        update_hour.value = existing_values[1]
    }

    // Append new input fields to the container
    cs_form_group_div.appendChild(update_text)
    cs_form_group_div.appendChild(update_hour)
    cs_form_group_div.appendChild(remove_update_btn)

    // dynamicInputsContainer.appendChild(update_text);
    // dynamicInputsContainer.appendChild(update_hour);
    // dynamicInputsContainer.appendChild(document.createElement('br'))
    dynamicInputsContainer.appendChild(cs_form_group_div)

    update_hour.addEventListener('keyup', function (event) {
        calculate_hours()
    })
    update_hour.addEventListener('wheel', function (event) {
        event.preventDefault()
    })
    update_text.addEventListener('keyup', function (event) {
        calculate_hours()
    })

    remove_update_btn.addEventListener('click', function (){
        let no_id = remove_update_btn.id.split('-')
        no_id = no_id[no_id.length-1]
        document.getElementById(`cs-form-group-${no_id}`).remove()
        calculate_hours()
    })
    count++

}

function calculate_hours(){
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
    if(updates_json_input_field != null){
        updates_json_input_field.innerText = JSON.stringify(updates)
    }

    // console.log('updates: ', JSON.stringify(updates))
    let total_hour = 0.0
    all_times.forEach((time_of_one)=>{
        total_hour += time_of_one.value?parseFloat(time_of_one.value):0
        console.log(time_of_one.value)
    })
    document.getElementById('id_hours').value = total_hour
    document.getElementById('show-hour').textContent = total_hour.toString()
}