// Frontend encryption/decryption functions for e2e encryption
// These functions handle both encryption and decryption of private messages

export async function encryptText(text, key) {
  try {
    if (!key || !text) {
      throw new Error('Missing key or text')
    }

    // Convert base64 key to CryptoKey
    const rawKey = Uint8Array.from(atob(key), (c) => c.charCodeAt(0))
    const cryptoKey = await window.crypto.subtle.importKey(
      'raw',
      rawKey,
      { name: 'AES-GCM' },
      false,
      ['encrypt']
    )

    // Generate a random IV
    const iv = window.crypto.getRandomValues(new Uint8Array(12))

    // Encrypt the text
    const encodedText = new TextEncoder().encode(text)
    const encryptedData = await window.crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      cryptoKey,
      encodedText
    )

    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encryptedData.byteLength)
    combined.set(iv)
    combined.set(new Uint8Array(encryptedData), iv.length)

    // Convert to base64 for transmission
    return btoa(String.fromCharCode(...combined))
  } catch (error) {
    console.error('Encryption failed:', error)
    throw new Error('Encryption failed')
  }
}

export async function decryptText(encryptedText, key) {
  try {
    if (!key || !encryptedText) {
      throw new Error('Missing key or encrypted text')
    }

    // Convert base64 key to CryptoKey
    const rawKey = Uint8Array.from(atob(key), (c) => c.charCodeAt(0))
    const cryptoKey = await window.crypto.subtle.importKey(
      'raw',
      rawKey,
      { name: 'AES-GCM' },
      false,
      ['decrypt']
    )

    // Decode the base64 encrypted text
    const encryptedData = Uint8Array.from(atob(encryptedText), (c) =>
      c.charCodeAt(0)
    )

    // Extract IV (first 12 bytes) and ciphertext
    const iv = encryptedData.slice(0, 12)
    const ciphertext = encryptedData.slice(12)

    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      cryptoKey,
      ciphertext
    )

    // Convert the decrypted data to text
    return new TextDecoder().decode(decryptedData)
  } catch (error) {
    console.error('Decryption failed:', error)
    throw new Error('Decryption failed')
  }
}
