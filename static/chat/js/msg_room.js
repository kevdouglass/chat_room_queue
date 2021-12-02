const roomName = JSON.parse(document.getElementById('room-name').textContent);
const chatLog = document.getElementById("chat-log");
//this_user-name
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
/* Handle Client Side WebSocket Connection */
const BASE_URL = "ws://"+window.location.host;
const ENDPOINT = "/ws/chat/rooms/";
// const chatSocket = new WebSocket( BASE_URL+ENDPOINT+roomName+"/" );
// console.log("New ChatSocket(", BASE_URL+ENDPOINT+roomName+"/" ,")")
class ClientsList {
    constructor() {
        console.log("New Client!");
        this.client_list = {};
        this.saveClient = this.setSavedClient.bind(this);
    }
    setSavedClient(username, client){
        console.log("[",client,"]: \tSaving User: ", username, " to ClientList")
        this.client_list[ username ] = client;
    }
}

// var chatForm = document.getElementById('chatForm')
const clients = new ClientsList();
var client_from_backend = undefined;

const chatSocket = new WebSocket(
    BASE_URL +
    ENDPOINT +
    roomName + '/'
);
chatSocket.onopen = function(ws_event){
    // if self.postMessage
    client_from_backend = ws_event;

    // console.log("\n\nws.onOpen() EVENT:", ws_event  )    // logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
    const logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);

        const waitingUserQueueDiv = document.getElementById('waiting_queue');
        var waitingUserNode = document.createElement('a');
        waitingUserNode.innerText = JSON.stringify(logged_in_user_id) + "\n";
        waitingUserNode.classList.add('list-group-item', 'list-group-item-action');
        waitingUserQueueDiv.appendChild(waitingUserNode);

}
// chatSocket.co

// once client side wS recieves a message,
chatSocket.onmessage = function(event) {
    /** When user sends message through input field, create new div element and send to other Ws functions */
    // chatSocket.co
    console.log("onMessage: ", event)
    const data = JSON.parse(event.data);
    
    clients.setSavedClient(data['user_username'], chatSocket );
    console.log("Clients: ", clients);
    
    //console
    // if (data['chat_msg']){
    // }
    

        const messageNode = document.createElement('div');
        user_username = data['user_username']
        const user_user_id = data['user_id']
        const waiting_queue_users = data['user_queue_nodes'];

        const logged_in_user_id = JSON.parse(document.getElementById('request_user_id').textContent);
        // const all_other_users = data['all_other_users'];
        // const waitingUserQueueDiv = document.getElementById('waiting_queue');
  
            const user_name_span = document.createElement('small')
            user_name_span.innerText = '['+user_username+']: \t' + data['message']; //+ " , " + user_user_id;
            user_name_span.classList.add('badge');
            // messageNode.innerText = '['+user_username+']: ' + data['message'];
            // <span class="badge badge-light">4</span>
            // messageNode.innerHTML =  //.classList.add('')
            messageNode.appendChild(user_name_span);
    // messageNode.className = 'message'; // insead create class list item of '.message sender' or '.message receiver'
    if (isMessageSender(user_user_id, logged_in_user_id)){
        messageNode.classList.add('message', 'sender');
    }else{
        messageNode.classList.add('message', 'receiver');
    }
    chatLog.appendChild( messageNode );

    console.log("WS.onMessage() : {END}")
    if (document.getElementById('emptyTextNode')){
        document.getElementById('emptyTextNode').remove();
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
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    const request_user_id = JSON.parse(document.getElementById('request_user_id').textContent)
    const request_user_username = JSON.parse(document.getElementById('request_user_username').textContent)

    // print("Sending MESSAGE + USER to BACKEND.")
    // 'user_username' : user_username,
    console.log("chatSocket, ",chatSocket)
    console.log("clients: ",clients);
    // clients[user_username].send(JSON.stringify({
    //   'message': "Tessssssstttt12344",  
    // }));
    chatSocket.send(JSON.stringify({
        'message': message, 
        // 'waiting_queue_users': request_user_id, 
    }));
    messageInputDom.value = '';
};