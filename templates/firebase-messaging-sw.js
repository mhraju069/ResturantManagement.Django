importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

// Configured dynamically via Django template rendering
const firebaseConfig = {
    apiKey: "{{ firebase_config.apiKey }}",
    authDomain: "{{ firebase_config.authDomain }}",
    projectId: "{{ firebase_config.projectId }}",
    storageBucket: "{{ firebase_config.storageBucket }}",
    messagingSenderId: "{{ firebase_config.messagingSenderId }}",
    appId: "{{ firebase_config.appId }}",
    measurementId: "{{ firebase_config.measurementId }}"
};

if (firebaseConfig.apiKey) {
    firebase.initializeApp(firebaseConfig);
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage((payload) => {
        console.log('[firebase-messaging-sw.js] Received background message ', payload);
        const notificationTitle = payload.notification.title;
        const notificationOptions = {
            body: payload.notification.body,
            icon: payload.notification.icon || '/static/speed_icon.png',
            data: payload.data
        };

        self.registration.showNotification(notificationTitle, notificationOptions);
    });
}
