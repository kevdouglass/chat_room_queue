
class ClientsList {
    constructor() {
        // console.log("New Client!");
        this.client_list = {};
        this.saveClient = this.setSavedClient.bind(this);
    }
    setSavedClient(client_username, client_id){
        // console.log("[",client_id,"]: \tSaving User: ", client_username, " to ClientList")
        this.client_list[ client_id ] = client_username;
    }
    getClients(){
        return this.client_list;
    }
    getCount(){
        var count = 0
        for(const key in this.client_list){
            if (this.client_list.hasOwnProperty(key)){
                count++;
            }
        }
        return count;
    }
    UserQDisplay(){
        // console.log("Client List: ",this.client_list);
        for (var key in this.client_list){
            var user = this.client_list[key];
            console.log(user)
            // this.pushUserQDisplay(user.username, user.id);
        }
    }
    updateUserQDisplay(live_userData, removed_userData){
        console.log("[Update] UserQueue");
        console.log(", [removed_userData] ", removed_userData)
        var remove_list_group_item = document.getElementById('user-'+removed_userData.id).remove();
    }

    pushUserQDisplay(client_username, client_id){
        console.log("[PUSH]"+ client_username +" UserQueue");    
        var cur_user = document.querySelectorAll('#user-'+client_id);
            // var isLiveBadge = document.createElement('span');
            // isLiveBadge.classList.add('badge', 'badge-light');
            var list_group_item = document.getElementById('user-'+client_id);
            if (!list_group_item){
                
                var list_group_item = document.createElement('a');
                list_group_item.setAttribute('id','user-'+client_id);
                list_group_item.classList.add('list-group-item','list-group-item-action');
                list_group_item.innerHTML = client_username;
                
                // var profile_avatar = document.createElement('div');
                // profile_avatar.classList.add('profile_avatar');
                
                // list_group_item.appendChild(isLiveBadge)
                // // console.log(list_group_item)
                // profile_avatar.appendChild(list_group_item);
                // WAITING_Q.appendChild(profile_avatar);
                wq.appendChild(list_group_item)
                return;
            }
        
    }
    // updateClient
}

/* Handle Client Side WebSocket Connection */
const BASE_URL = "ws://"+window.location.host;
const ENDPOINT = "/ws/chat/rooms/";
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const connected_clients = new ClientsList();
var client_from_backend = undefined;
const chatSocket = new WebSocket(
    BASE_URL +
    ENDPOINT +
    roomName + '/'
);
const userNotifySocket = new WebSocket(
    BASE_URL +
    ENDPOINT +
    roomName + '/'
    );
    const chatLog = document.getElementById("chat-log");
    const wq = document.getElementById('waiting_queue')
    const request_user_id = JSON.parse(document.getElementById('request_user_id').textContent)
    const request_user_username = JSON.parse(document.getElementById('request_user_username').textContent)

//this_user-name
var PREV_LENGTH = 0;
var user_username = undefined;
console.warn("New Room Name: {"+ roomName +"}");

/** TODO */
// create function to return True/False and handle processing in ChatSocket.onMessage
if (!(chatLog.hasChildNodes()) || chatLog.childNodes.length >= 1 ){
    if(!(document.getElementsByClassName('message')) ){

        const emptyTextNode = document.createElement('h3');
        emptyTextNode.id = 'emptyTextNode';
        emptyTextNode.innerText = 'No Messages';
        emptyTextNode.className = 'emptyTextNode';
        chatLog.appendChild(emptyTextNode);
    }
}

function isMessageSender(ws_user_id, logged_in_user_id){
    return (ws_user_id === logged_in_user_id)
}

        
function createMessageNode(message, sender, user_user_id ){


    const this_user_user_id = JSON.parse(document.getElementById('request_user_id').textContent);    
    
    const messageNode = document.createElement('div');
    const user_name_span = document.createElement('small');
    
    user_name_span.innerText = '['+sender+']:\n'; 
    user_name_span.style.fontSize = '6px';
    user_name_span.classList.add('badge');
    var msg_content = document.createElement('span');
    /** TODO */
    // msg_content.classList.add();
    messageNode.innerText = message; // insead create class list item of '.message sender' or '.message receiver'
    if (isMessageSender(user_user_id, this_user_user_id)){
        messageNode.classList.add('message', 'sender');
    }else{
        messageNode.classList.add('message', 'receiver');
    }

    msg_content.prepend(user_name_span);
    msg_content.appendChild(messageNode);
    messageNode.appendChild(user_name_span);
    chatLog.appendChild( messageNode );

    if (document.getElementById('emptyTextNode')){
        document.getElementById('emptyTextNode').remove();
    }
}


const fetchPath = (endpoint) => {
    return window.location.origin
            +window.location.pathname
            +endpoint;
}

        

userNotifySocket.onopen = function(ws_event){
    
    userNotifySocket.onmessage = function(event){
        let jsonData = JSON.parse(event.data)

        if(jsonData.kind == "userConnectedNotification"){
            connected_clients.pushUserQDisplay(jsonData.real_time_user.username, jsonData.real_time_user.id );
        }
        else if(jsonData.kind == "userDisconnectedNotification"){
            console.log("[userDisconnectNotification] ", jsonData );
            // removed_user
            if (jsonData.removed_user){

                connected_clients.updateUserQDisplay(jsonData.real_time_user, jsonData.removed_user)
            }
        }
    }
}

        
        


// once client side wS recieves a message,
chatSocket.onmessage = function(event) {
    /** When user sends message through input field, create new div element and send to other Ws functions */
    const data = JSON.parse(event.data);
    const user_user_id = data['user_id']
    const waiting_queue_users = data['real_time_users'];
    user_username = data['user_username'];
    
    if (data.count >= 0){
        if (data.message){
            createMessageNode(data.message, user_username, user_user_id);
        }    
    }
}


chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    // console.log("Sending MESSAGE + USER to BACKEND.")
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'message': message, 
    }));
    messageInputDom.value = '';
};