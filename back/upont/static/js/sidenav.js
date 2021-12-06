document.addEventListener("DOMContentLoaded", function(event) {

    const sidenav = document.querySelector('.sidenav');
    const sidenavLinks = document.querySelectorAll('.sidenav-link')
    const signoutLink = document.querySelector('.sidenav-last-link');
    const toggle = document.querySelector('.toggle')

    toggle.addEventListener('click', () =>{
        sidenav.classList.toggle('show-border');
        sidenavLinks.forEach(l=> l.classList.toggle('show-link'));
        signoutLink.classList.toggle('show-last-link');
    })

});