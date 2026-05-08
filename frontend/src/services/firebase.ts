import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyCCxJlOakQVJNJ30jR9ilCRJc3871fdLCI",
  authDomain: "solid-altar-495705-q5.firebaseapp.com",
  projectId: "solid-altar-495705-q5",
  storageBucket: "solid-altar-495705-q5.firebasestorage.app",
  messagingSenderId: "258840388638",
  appId: "1:258840388638:web:b554e237ac65cb9ea4fa0f",
  measurementId: "G-44CL58BKF1"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
