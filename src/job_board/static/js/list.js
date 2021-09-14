window.onload = () => {
    console.log('asdf')
    let filterToggleButton = document.createElement('BUTTON')
    filterToggleButton.innerHTML = '>>'
    filterToggleButton.className = "btn btn-filter"

    let mainContent = document.getElementById('content-main')
    mainContent.style.position = 'relative'
    mainContent.prepend(filterToggleButton)

    let filter = document.getElementById('changelist-filter')

    filterToggleButton.onclick = () => {
        if (filter.style.display === 'none') {
            filter.style.display = 'block'
            filterToggleButton.innerHTML = '>>'
        } else {
            filter.style.display = 'none'
            filterToggleButton.innerHTML = '<<'
        }
    }

}