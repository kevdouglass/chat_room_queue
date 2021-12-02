document.querySelector('#room-name-input').focus();
document.querySelector('#room-name-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#room-name-submit').click();
    }
};
                
// const client = 
                /** Handled in Django Forms.py instead of Javascript.. */
                // document.querySelector('#room-name-submit').onclick = function(e) {
                //     var roomName = document.querySelector('#room-name-input').value;
                //     console.log("THISSSSSS...")
                    
                //     window.location.pathname = '/chat/' + roomName + '/';
                //     console.warn("New Page: ", window.location);
                // };