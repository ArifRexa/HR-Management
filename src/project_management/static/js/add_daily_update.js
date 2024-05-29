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

// icons
const git_icon = `<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 496 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/></svg>`

document.addEventListener("DOMContentLoaded", function () {
    let formType = window.location.pathname.split('/')
    formType = formType[formType.length - 2]
    console.log(formType)

    document.getElementsByClassName('form-row field-updates_json')[0].getElementsByTagName('label')[0].innerText = 'Updates:'

    // document.getElementById('id_hours').readonly = true
    // employee view
    if (document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0] != null){
        console.log('cannot edit updates')
        let updates = document.getElementsByClassName('form-row field-updates_json')[0].getElementsByClassName('readonly')[0].innerText
        updates = JSON.parse(updates)
        let html_updates = "<ol name='updates_json'>"
        for (i=1; i<=updates.length; i++){
            let git_link = updates[i-1][2] ? ` - <a href="${updates[i-1][2]}">${git_icon}</a>` : ""
            html_updates += `<li> ${updates[i-1][0]} - ${updates[i-1][1]}H  ${git_link} </li>`
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
    // admin view
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
            // document.getElementsByClassName('form-row field-update')[0].style.display = 'None'
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
    update_text.required = false;

    const update_github_link = document.createElement("textarea");
    update_github_link.type = "text";
    update_github_link.name = "input_github_link";
    update_github_link.id = `input_github_link-${count}`;
    update_github_link.className = "cs-form-control-text fa-solid fa-code-branch"

    update_github_link.placeholder = "Commit Link";
    update_github_link.required = true;

    const update_hour = document.createElement("input");
    update_hour.type = "number";
    update_hour.name = "input_time";
    update_hour.id = `input_time-${count}`;
    update_hour.className = "cs-form-control"
    update_hour.placeholder = "Time";
    update_hour.required = true
    update_hour.max = '2.0'
    update_hour.min = "0.0"
    update_hour.value = '0.0'

    const remove_update_btn = document.createElement('button')
    remove_update_btn.type = "button"
    remove_update_btn.id = `remove-button-${count}`
    remove_update_btn.textContent = "Remove"
    remove_update_btn.className = 'remove-update-btn'

    if (existing_values != null){
        update_text.value = existing_values[0]
        update_hour.value = existing_values[1]
        update_github_link.value = existing_values[2] ? existing_values[2] : ""
    }

    // Append new input fields to the container
    cs_form_group_div.appendChild(update_text)
    cs_form_group_div.appendChild(update_github_link)
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
    update_github_link.addEventListener('keyup', function (event){
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
    all_github_links = document.getElementsByName('input_github_link')
    all_times = document.getElementsByName('input_time')
    disable_save_if_no_commit_link()
    // let json__ = {}
    let updates = []
    for (i=0; i<all_updates.length; i++){
        // console.log(all_updates[i].value.toString())
        // console.log(all_times[i].value.toString())

        let individual_update = [all_updates[i].value, all_times[i].value, all_github_links[i].value]
        updates.push(individual_update)
    }
    if(updates_json_input_field != null){
        updates_json_input_field.innerText = JSON.stringify(updates)
    }

    // console.log('updates: ', JSON.stringify(updates))
    let total_hour = 0.0
    all_times.forEach((time_of_one)=>{
        if (time_of_one.value && time_of_one.value > 4.0){
            time_of_one.value = 4.0
        }
        else if (time_of_one.value && time_of_one.value < 0){
            time_of_one.value = 0.0
        }

        total_hour += time_of_one.value?parseFloat(time_of_one.value):0
        console.log(time_of_one.value)
    })
    total_hour = total_hour.toFixed(2)
    document.getElementById('id_hours').value = total_hour
    document.getElementById('show-hour').textContent = total_hour.toString()
}

function disable_save_if_no_commit_link(){
    let all_github_links = document.getElementsByName('input_github_link')
    let submit_block = document.getElementsByClassName('submit-row')[0]
    // let update_block = document.getElementsByClassName('form-row field-updates_json')[0]
    // let para=document.createElement('div');
    //
    // let node=document.createTextNode('Commit link is mandatory!!');
    // para.appendChild(node);
    // console.log(submit_block.children)
    for (i=0; i<all_github_links.length; i++){
        console.log(all_github_links[i].value == '')
            if(all_github_links[i].value == ''){
                // submit_block.children
                submit_block.childNodes.forEach((buttons) => {
                    buttons.disabled = true
                })
                // update_block.insertBefore(para, update_block.firstChild);
                // submit_block.style.display = 'none';
                break;
            }
            else{
                submit_block.childNodes.forEach((buttons) => {
                    buttons.disabled = false
                })
                // submit_block.style.display = 'block';
            }
    }
}