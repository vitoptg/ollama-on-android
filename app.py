from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)
conversation_histories = {}



HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Шутки от ИИшки</title>

<style>
*{
margin:0;
padding:0;
box-sizing:border-box;
font-family:Arial,sans-serif;
}

body{
height:100vh;
display:flex;
background:#212121;
color:white;
overflow:hidden;
}

.sidebar{
width:260px;
background:#171717;
border-right:1px solid #333;
display:flex;
flex-direction:column;
padding:10px;
gap:10px;
}

.logo{
font-size:20px;
font-weight:bold;
padding:10px;
}

#newChat{
background:#2d2d2d;
border:none;
color:white;
padding:12px;
cursor:pointer;
}

#modelSelect{
background:#2d2d2d;
color:white;
border:none;
padding:10px;
}

#history{
flex:1;
overflow:auto;
display:flex;
flex-direction:column;
gap:5px;
}

.chatItem{
padding:10px;
background:#2a2a2a;
cursor:pointer;
}

.chatItem:hover{
background:#353535;
}

.main{
flex:1;
display:flex;
flex-direction:column;
}

.chat{
flex:1;
overflow-y:auto;
padding:20px;
display:flex;
flex-direction:column;
gap:15px;
}

.message{
max-width:85%;
padding:14px;
border-radius:12px;
white-space:pre-wrap;
}

.user{
align-self:flex-end;
background:#3b82f6;
}

.bot{
align-self:flex-start;
background:#2f2f2f;
}

.input-area{
padding:20px;
display:flex;
gap:10px;
border-top:1px solid #333;
}

textarea{
flex:1;
background:#2f2f2f;
border:none;
color:white;
padding:14px;
resize:none;
outline:none;
height:60px;
}

button{
background:#10a37f;
border:none;
color:white;
padding:0 20px;
cursor:pointer;
}
@media (max-width: 768px){

body{
    flex-direction:column;
}

.sidebar{
    width:100%;
    height:130px;
    border-right:none;
    border-bottom:1px solid #333;
    flex-shrink:0;
}

.logo{
    font-size:18px;
    text-align:center;
}

#history{
    display:flex;
    flex-direction:row;
    overflow-x:auto;
    overflow-y:hidden;
    gap:8px;
}

.chatItem{
    min-width:150px;
    white-space:nowrap;
}

.main{
    height:calc(100vh - 130px);
}

.chat{
    padding:12px;
}

.message{
    max-width:95%;
    font-size:15px;
}

.input-area{
    padding:10px;
}

textarea{
    height:50px;
    font-size:16px;
}

button{
    min-width:70px;
}

#modelSelect{
    width:100%;
}
}
</style>
</head>
<body>

<div class="sidebar">

<div class="logo">
Шутки от ИИшки
</div>

<button id="newChat">
Новый чат
</button>

<select id="modelSelect"></select>

<div id="history"></div>

</div>

<div class="main">

<div class="chat" id="chat"></div>

<div class="input-area">
<textarea id="prompt"></textarea>
<button onclick="sendMessage()">
Отпр
</button>
</div>

</div>

<script>

let chats=
JSON.parse(localStorage.getItem('chats')||'{}');

let currentChat=null;

const historyDiv=document.getElementById('history');
const chat=document.getElementById('chat');

function saveChats(){
localStorage.setItem(
'chats',
JSON.stringify(chats)
);
}

function renderHistory(){

historyDiv.innerHTML='';

for(const id in chats){

const div=document.createElement('div');

div.className='chatItem';

div.textContent=
chats[id].title;

div.onclick=()=>openChat(id);

historyDiv.appendChild(div);
}
}

function renderMessages(){

chat.innerHTML='';

if(!currentChat) return;

chats[currentChat].messages.forEach(msg=>{

const div=document.createElement('div');

div.className=
'message '+msg.role;

div.textContent=
msg.content;

chat.appendChild(div);

});

chat.scrollTop=
chat.scrollHeight;
}

function openChat(id){

currentChat=id;

renderMessages();
}

document.getElementById(
'newChat'
).onclick=()=>{

const id=
Date.now().toString();

chats[id]={
title:'Новый чат',
messages:[]
};

currentChat=id;

saveChats();

renderHistory();

renderMessages();

};

async function loadModels(){

const res=
await fetch('/models');

const data=
await res.json();

const select=
document.getElementById(
'modelSelect'
);

select.innerHTML='';

(data.models||[]).forEach(model=>{

const option=
document.createElement(
'option'
);

option.value=model.name;

option.textContent=
model.name;

select.appendChild(option);

});
}

async function sendMessage(){

if(!currentChat) return;

const input=
document.getElementById(
'prompt'
);

const text=
input.value.trim();

if(!text) return;

input.value='';

chats[currentChat].messages.push({
role:'user',
content:text
});

if(
chats[currentChat].messages.length===1
){
chats[currentChat].title=
text.substring(0,25);
}

renderHistory();
renderMessages();
saveChats();

const res=
await fetch('/chat',{

method:'POST',

headers:{
'Content-Type':'application/json'
},

body:JSON.stringify({

prompt:text,

chat_id:currentChat,

model:
document.getElementById(
'modelSelect'
).value

})

});

const data=
await res.json();

chats[currentChat].messages.push({

role:'bot',

content:data.response

});

saveChats();

renderMessages();
}

document.getElementById(
'prompt'
).addEventListener(
'keydown',
e=>{

if(
e.key==='Enter'
&&
!e.shiftKey
){

e.preventDefault();

sendMessage();

}

});

loadModels();

renderHistory();

if(
Object.keys(chats).length===0
){

document.getElementById(
'newChat'
).click();

}
else{

currentChat=
Object.keys(chats)[0];

renderMessages();

}

</script>

</body>
</html>
"""
@app.route('/models')
def models():
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags")
        return jsonify(response.json())
    except:
        return jsonify({"models": []})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json

    chat_id = data.get("chat_id", "default")
    model = data.get("model", "qwen2.5:0.5b")
    user_message = data["prompt"]

    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = []

    history = conversation_histories[chat_id]

    history.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": model,
        "messages": history,
        "stream": False
    }

    response = requests.post(
        "http://127.0.0.1:11434/api/chat",
        json=payload
    )

    bot_response = response.json()["message"]["content"]

    history.append({
        "role": "assistant",
        "content": bot_response
    })

    return jsonify({
        "response": bot_response
    })



@app.route('/')
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )