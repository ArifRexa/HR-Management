document.addEventListener("DOMContentLoaded",function(){
    console.log("Running")
    setTimeout(function(){
        window.location.reload();
     }, 300000);


    const commentPopups = document.querySelectorAll('.comment-popup');

     commentPopups.forEach(popup => {
         popup.addEventListener('mouseover', function (e) {
             const fullComment = e.target.getAttribute('data-full-comment');
 
             const tooltip = document.createElement('div');
             tooltip.className = 'comment-tooltip';
             tooltip.innerText = fullComment;
 
             document.body.appendChild(tooltip);
             const rect = e.target.getBoundingClientRect();
             tooltip.style.left = `${rect.left + window.scrollX}px`;
             tooltip.style.top = `${rect.bottom + window.scrollY}px`;
 
             // Remove tooltip on mouseout
             e.target.addEventListener('mouseout', function () {
                 tooltip.remove();
             }, { once: true });
         });
     });
})