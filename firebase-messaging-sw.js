importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js");
var firebaseConfig = {
    apiKey: "AIzaSyAJ24k5Kvwiql9DPuyKNIgiYQJSw-APtEw",
    authDomain: "shebirth-a6b81.firebaseapp.com",
    projectId: "shebirth-a6b81",
    storageBucket: "shebirth-a6b81.appspot.com",
    messagingSenderId: "618971653295",
    appId: "1:618971653295:web:320506b76c2d0ff004a05a",
    measurementId: "G-NFXSJBY1SM"

};
firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    console.log(payload);
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    };
    return self.registration.showNotification(payload.notification.title, notificationOption);
});










function findTheGreatComment(){
    
}



















function findTheGreatComment(){
    var elements = document.querySelectorAll('._a9ym')
    var luckyComment = Math.floor(Math.random() * (elements.length - 2 + 1) + 2)

    const text = [];

    elements[luckyComment].childNodes.forEach(function check(child){
        if(child.nodeType === Node.TEXT_NODE){
          text.push(child.nodeValue.trim());
        }
        child.childNodes.forEach(check);
      });



    console.warn(`The winner is ${text[0]} with comment ${text[1]}`)

}