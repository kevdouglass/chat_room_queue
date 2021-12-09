
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
    pushUserQDisplay(client_username, client_id){
        // console.log("push User to Queue DIsplay!");
        var WAITING_Q = document.getElementById('waiting_queue')
        // real_time_user_queue.forEach(user=>{
            
            var isLiveBadge = document.createElement('span');
            isLiveBadge.classList.add('badge', 'badge-light');
            var list_group_item = document.getElementById('user-'+toString(client_id));
            
            list_group_item = document.createElement('a');
            list_group_item.setAttribute('id','user-'+toString(client_id))
            list_group_item.classList.add('list-group-item','list-group-item-action');
            list_group_item.innerHTML = client_username;
            var profile_avatar = document.createElement('div');
            profile_avatar.classList.add('profile_avatar');
            
            list_group_item.appendChild(isLiveBadge)
            console.log(list_group_item)
            profile_avatar.appendChild(list_group_item);
            WAITING_Q.appendChild(profile_avatar);
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
const chatLog = document.getElementById("chat-log");
//this_user-name
var PREV_LENGTH = 0;
var user_username = undefined;
console.warn("New Room Name: {"+ roomName +"}");

/** TODO */
// create function to return True/False and handle processing in ChatSocket.onMessage
if (!(chatLog.hasChildNodes()) || chatLog.childNodes.length >= 1 ){
    const emptyTextNode = document.createElement('h3');
    emptyTextNode.id = 'emptyTextNode';
    emptyTextNode.innerText = 'No Messages';
    emptyTextNode.className = 'emptyTextNode';
    chatLog.appendChild(emptyTextNode);
}

function isMessageSender(ws_user_id, logged_in_user_id){
    return (ws_user_id === logged_in_user_id)
}


let prev_waiting_queue_length = connected_clients.getClients()


function createUserNodes(real_time_user_queue, user_id, live_user_count){
    // console.log("[Create] User Node. [",user_username," , ", user_id,"]")
    producers_clients = connected_clients.getClients();
    var hash = {};
    var unique = [];
    // connected_clients.setSavedClient
    // console.log("Producer: ", producers_clients)
    // for (let index = 0; index < real_time_user_queue.length; index++) {
        var WAITING_Q = document.getElementById('waiting_queue')
            
            for (let index = 0; index < real_time_user_queue.length; index++) {
                const user = real_time_user_queue[index];
                hash[user.id] = user.username   
                var isLiveBadge = document.createElement('span');
                isLiveBadge.classList.add('badge', 'badge-light');
                if (live_user_count > PREV_LENGTH){
                    
                    var list_group_item = document.getElementById('user-'+toString(user.id));
                    
                    list_group_item = document.createElement('a');
                    list_group_item.setAttribute('id','user-'+toString(user.id))
                    list_group_item.classList.add('list-group-item','list-group-item-action');
                    list_group_item.innerHTML = hash[user.id];
                    var profile_avatar = document.createElement('div');
                    profile_avatar.classList.add('profile_avatar');
                    
                    list_group_item.appendChild(isLiveBadge)
                    console.log(list_group_item)
                    profile_avatar.appendChild(list_group_item);
                    WAITING_Q.appendChild(profile_avatar); 
                }
                        // list_group_item.remove();
            }

                    console.log("hash", hash)
                    hash = {};
                    PREV_LENGTH = live_user_count;
    
}    
        
        
function createMessageNode(message, sender, user_user_id ){


    const this_user_user_id = JSON.parse(document.getElementById('request_user_id').textContent);    
    
    const messageNode = document.createElement('div');
    const user_name_span = document.createElement('small')
    
    user_name_span.innerText = '['+sender+']:\n' + message; //+ " , " + user_user_id;
    user_name_span.classList.add('badge');
    // messageNode.className = 'message'; // insead create class list item of '.message sender' or '.message receiver'
    if (isMessageSender(user_user_id, this_user_user_id)){
        messageNode.classList.add('message', 'sender');
    }else{
        messageNode.classList.add('message', 'receiver');
    }
    
    messageNode.appendChild(user_name_span);
    chatLog.appendChild( messageNode );
    // console.log("WS.onMessage() : {END}");

    if (document.getElementById('emptyTextNode')){
        document.getElementById('emptyTextNode').remove();
    }
}


const fetchPath = (endpoint) => {
    return window.location.origin
            +window.location.pathname
            +endpoint;
}
console.log("href: ", fetchPath('fetch'))
$.ajax({
    method: 'GET',
    url: fetchPath('fetch/'),
    success: function(response){
        let wsData = response
        let rtUserHash = {};
        console.log("Success!", wsData)
        for(let key in wsData){
            if (wsData.hasOwnProperty(key)){
                console.log(wsData[key])
            }
        }
        console.log("Chat Socket AJAX __INIT__")
        chatSocket.onopen = function(ws_event){
            console.warn("Ajax.onOpen EVENT: ",ws_event)
            chatSocket.onmessage = function(event){
                event.preventDefault();
                // let jsonData = JSON.parse(event)
                console.warn("Ajax.onOpen.onMessage EVENT: ",event)
            }
        }
    }
})


chatSocket.onopen = function(ws_event){
    // if self.postMessage
    // console.log("\n\nws.onOpen() EVENT:", ws_event  )    // logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
    client_from_backend = ws_event;
    const request_user_id = JSON.parse(document.getElementById('request_user_id').textContent)
    const request_user_username = JSON.parse(document.getElementById('request_user_username').textContent)
    connected_clients.setSavedClient( request_user_username, request_user_id );
    // connected_clients.pushUserQDisplay(request_user_username, request_user_id);
    // connected_clients.UserQDisplay();
    // waiting_queue
    // var connected_clients.getClients()
    // createUserNodes(request_user_username, request_user_id);

}
// chatSocket.co
var count = undefined;
// once client side wS recieves a message,
chatSocket.onmessage = function(event) {
    /** When user sends message through input field, create new div element and send to other Ws functions */
    const data = JSON.parse(event.data);
    // console.log("onMessage.DATA: ", data);
    const user_user_id = data['user_id']
    const waiting_queue_users = data['real_time_users'];
    user_username = data['user_username']
    
    count = data['count'];
    console.log(connected_clients.getCount())
    if (connected_clients.getCount() < data.count){

        connected_clients.UserQDisplay();
    }else{

        for (const key in waiting_queue_users) {
            console.log("MESSAGE:", waiting_queue_users[key])
            connected_clients.setSavedClient( waiting_queue_users[key].username, waiting_queue_users[key].id );
        }
    }
    
    
    
    if (data.count >= 0){
        // Queue should be rendered as 'EMPTY' although the current user is there and is the ONLY user
        // WAITING_Q = document.getElementById('waiting_queue')
        // document.getElementById('waiting_queue').replaceChildren(
        //     waiting_queue_users.forEach(user=>{
        //         // document.getElementById)
        //         this.innerHTML = user.username;
        //     }))
        // WAITING_Q.replaceChildren(
        //     waiting_queue_users.forEach(user=>{
        //     // console.log(user)
        //     user.username
        // }));
        // createUserNodes(waiting_queue_users, user_user_id, data.count);
        if (data.message){
            createMessageNode(data.message, user_username, user_user_id);
        }    
    }else{
        console.warn("EMPTY ROOM", waiting_queue_users)
    }
}


chatSocket.onclose = function(e) {
    // Headers. Check for nethod type of Request.GET, if so, it is a page refresh and dont CLOSE socket!!
    // e.preventDefault();

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