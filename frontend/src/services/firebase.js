import { initializeApp } from 'firebase/app'
import {
  GoogleAuthProvider,
  browserLocalPersistence,
  createUserWithEmailAndPassword,
  getAuth,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
} from 'firebase/auth'
import {
  doc,
  getDoc,
  initializeFirestore,
  serverTimestamp,
  setDoc,
  updateDoc,
} from 'firebase/firestore'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

const missingConfig = Object.entries(firebaseConfig).some(([, value]) => !value)
const firebaseApp = missingConfig ? null : initializeApp(firebaseConfig)
export const auth = firebaseApp ? getAuth(firebaseApp) : null
export const db = firebaseApp
  ? initializeFirestore(firebaseApp, { experimentalAutoDetectLongPolling: true })
  : null
export const googleProvider = new GoogleAuthProvider()

export function requireFirebase() {
  if (!auth || !db) {
    throw new Error('Firebase is not configured. Add the VITE_FIREBASE_* values to frontend/.env.')
  }
}

export async function configureAuthPersistence() {
  requireFirebase()
  await setPersistence(auth, browserLocalPersistence)
}

export function profileRef(uid) {
  requireFirebase()
  return doc(db, 'users', uid)
}

export async function getUserProfile(uid) {
  const snapshot = await getDoc(profileRef(uid))
  return snapshot.exists() ? snapshot.data() : null
}

export async function createUserProfile(user, name = '') {
  const ref = profileRef(user.uid)
  const existing = await getDoc(ref)
  if (existing.exists()) return existing.data()

  const profile = {
    name: name || user.displayName || '',
    email: user.email || '',
    onboardingCompleted: false,
    onboardingStep: 'profile',
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  }
  await setDoc(ref, profile)
  return profile
}

export async function updateOnboardingStep(uid, onboardingStep, data = {}) {
  await updateDoc(profileRef(uid), {
    ...data,
    onboardingStep,
    updatedAt: serverTimestamp(),
  })
}

export async function completeOnboarding(uid, data = {}) {
  await updateDoc(profileRef(uid), {
    ...data,
    onboardingCompleted: true,
    onboardingStep: 'complete',
    updatedAt: serverTimestamp(),
  })
}

export async function signupWithEmail(name, email, password) {
  requireFirebase()
  const credential = await createUserWithEmailAndPassword(auth, email, password)
  if (name) await updateProfile(credential.user, { displayName: name })
  const profile = await createUserProfile(credential.user, name)
  return { user: credential.user, profile }
}

export async function loginWithEmail(email, password) {
  requireFirebase()
  const credential = await signInWithEmailAndPassword(auth, email, password)
  const profile = await createUserProfile(credential.user)
  return { user: credential.user, profile }
}

export async function loginWithGoogle() {
  requireFirebase()
  const credential = await signInWithPopup(auth, googleProvider)
  const profile = await createUserProfile(credential.user)
  return { user: credential.user, profile }
}

export function logout() {
  requireFirebase()
  return signOut(auth)
}

export function resetPassword(email) {
  requireFirebase()
  return sendPasswordResetEmail(auth, email)
}
