import os
from PIL import Image
from cryptography.fernet import Fernet
import cryptography
import tkinter as tk
from tkinter import filedialog, messagebox
import wave
from pydub import AudioSegment

# Generate and save the encryption key (you only need to do this once)
def generate_key():
    key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)

# Check if the key file exists, if not, generate the key
if not os.path.exists("encryption_key.key"):
    generate_key()  # This will generate the key if not already present

# Load the encryption key
def load_key():
    with open("encryption_key.key", "rb") as key_file:
        key = key_file.read()
    return key

# Encrypt the message using the loaded key
def encrypt_message(message):
    cipher_suite = Fernet(load_key())
    encrypted_message = cipher_suite.encrypt(message.encode())
    return encrypted_message

# Decrypt the message using the loaded key
def decrypt_message(encrypted_message):
    cipher_suite = Fernet(load_key())
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
    return decrypted_message

# Encode the encrypted message into the image
def encode_image(image_path, text, output_path):
    encrypted_text = encrypt_message(text)
    binary_text = ''.join(format(byte, '08b') for byte in encrypted_text)

    image = Image.open(image_path)
    pixels = image.load()

    text_length = len(binary_text)
    width, height = image.size
    idx = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if idx < text_length:
                r = (r & 0xFE) | int(binary_text[idx])  # Embed bit in the red channel
                idx += 1
            if idx < text_length:
                g = (g & 0xFE) | int(binary_text[idx])  # Embed bit in the green channel
                idx += 1
            if idx < text_length:
                b = (b & 0xFE) | int(binary_text[idx])  # Embed bit in the blue channel
                idx += 1
            pixels[x, y] = (r, g, b)

    image.save(output_path)
    messagebox.showinfo("Success", f"Text successfully encoded in image and saved as {output_path}")

    return encrypted_text  # Return the encrypted text to display

# Decode the hidden message from the image
def decode_image(image_path):
    image = Image.open(image_path)
    pixels = image.load()

    binary_text = ''
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_text += str(r & 1)  # Extract LSB from red channel
            binary_text += str(g & 1)  # Extract LSB from green channel
            binary_text += str(b & 1)  # Extract LSB from blue channel

    encrypted_message = bytearray()
    for i in range(0, len(binary_text), 8):
        byte = binary_text[i:i+8]
        encrypted_message.append(int(byte, 2))

    try:
        decrypted_message = decrypt_message(bytes(encrypted_message))
        return encrypted_message, decrypted_message  # Return both encrypted and decrypted message
    except cryptography.fernet.InvalidToken:
        messagebox.showerror("Decryption Error", "Failed to decrypt the message. The image may be corrupted.")
        return None, None

# Encode the encrypted message into an audio file (using LSB in audio samples)
def encode_audio(audio_path, text, output_path):
    encrypted_text = encrypt_message(text)
    binary_text = ''.join(format(byte, '08b') for byte in encrypted_text)

    # Check file type and convert MP3 to WAV if necessary
    if audio_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_path)
        audio_path_wav = audio_path.replace(".mp3", ".wav")
        audio.export(audio_path_wav, format="wav")
        audio_path = audio_path_wav  # Use the temporary WAV file for encoding

    with wave.open(audio_path, 'rb') as audio:
        params = audio.getparams()
        frames = audio.readframes(params.nframes)
        audio.close()

    frame_bytes = bytearray(frames)
    text_length = len(binary_text)
    idx = 0

    for i in range(len(frame_bytes)):
        if idx < text_length:
            frame_bytes[i] = (frame_bytes[i] & 0xFE) | int(binary_text[idx])  # Embed bit
            idx += 1

    with wave.open(output_path, 'wb') as output_audio:
        output_audio.setparams(params)
        output_audio.writeframes(bytes(frame_bytes))

    messagebox.showinfo("Success", f"Text successfully encoded in audio and saved as {output_path}")

    return encrypted_text  # Return the encrypted text to display

# Decode the hidden message from the audio
def decode_audio(audio_path):
    # Check file type and convert MP3 to WAV if necessary
    if audio_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_path)
        audio_path_wav = audio_path.replace(".mp3", ".wav")
        audio.export(audio_path_wav, format="wav")
        audio_path = audio_path_wav  # Use the temporary WAV file for decoding

    with wave.open(audio_path, 'rb') as audio:
        params = audio.getparams()
        frames = audio.readframes(params.nframes)
        audio.close()

    frame_bytes = bytearray(frames)
    binary_text = ''
    for byte in frame_bytes:
        binary_text += str(byte & 1)  # Extract LSB

    encrypted_message = bytearray()
    for i in range(0, len(binary_text), 8):
        byte = binary_text[i:i+8]
        encrypted_message.append(int(byte, 2))

    try:
        decrypted_message = decrypt_message(bytes(encrypted_message))
        return encrypted_message, decrypted_message  # Return both encrypted and decrypted message
    except cryptography.fernet.InvalidToken:
        messagebox.showerror("Decryption Error", "Failed to decrypt the message. The audio may be corrupted.")
        return None, None

# GUI Functionality
def browse_image():
    filename = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    image_path_var.set(filename)

def browse_audio():
    filename = filedialog.askopenfilename(title="Select an Audio", filetypes=[("Audio Files", "*.wav;*.mp3")])
    audio_path_var.set(filename)

def encode():
    media_type = media_type_var.get()
    text = text_var.get()
    if not text:
        messagebox.showerror("Error", "Please provide a message.")
        return

    if media_type == 'Image':
        image_path = image_path_var.get()
        if not image_path:
            messagebox.showerror("Error", "Please select an image.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if not output_path:
            return
        encrypted_message = encode_image(image_path, text, output_path)

    elif media_type == 'Audio':
        audio_path = audio_path_var.get()
        if not audio_path:
            messagebox.showerror("Error", "Please select an audio file.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
        if not output_path:
            return
        encrypted_message = encode_audio(audio_path, text, output_path)

    encrypted_message_display.config(state=tk.NORMAL)
    encrypted_message_display.delete(1.0, tk.END)
    encrypted_message_display.insert(tk.END, encrypted_message)
    encrypted_message_display.config(state=tk.DISABLED)

def decode():
    media_type = media_type_var.get()
    if media_type == 'Image':
        image_path = filedialog.askopenfilename(title="Select an Encoded Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not image_path:
            return
        encrypted_message, decrypted_message = decode_image(image_path)

    elif media_type == 'Audio':
        audio_path = filedialog.askopenfilename(title="Select an Encoded Audio", filetypes=[("Audio Files", "*.wav;*.mp3")])
        if not audio_path:
            return
        encrypted_message, decrypted_message = decode_audio(audio_path)

    if encrypted_message and decrypted_message:
        decrypted_message_display.config(state=tk.NORMAL)
        decrypted_message_display.delete(1.0, tk.END)
        decrypted_message_display.insert(tk.END, decrypted_message)
        decrypted_message_display.config(state=tk.DISABLED)

def reset():
    text_var.set('')
    image_path_var.set('')
    audio_path_var.set('')
    encrypted_message_display.config(state=tk.NORMAL)
    encrypted_message_display.delete(1.0, tk.END)
    encrypted_message_display.config(state=tk.DISABLED)
    decrypted_message_display.config(state=tk.NORMAL)
    decrypted_message_display.delete(1.0, tk.END)
    decrypted_message_display.config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("Aayush Steganography Tool")

# Set background color and title font
root.configure(bg="lightblue")
title_label = tk.Label(root, text="Aayush Steganography Tool", font=("Helvetica", 18, "bold"), fg="gold", bg="lightblue")
title_label.pack(padx=10, pady=10)

media_type_var = tk.StringVar(value='Image')

media_type_frame = tk.Frame(root, bg="lightblue")
media_type_frame.pack(padx=10, pady=10)

image_radio = tk.Radiobutton(media_type_frame, text="Image", variable=media_type_var, value='Image', bg="lightblue")
image_radio.pack(side=tk.LEFT)

audio_radio = tk.Radiobutton(media_type_frame, text="Audio", variable=media_type_var, value='Audio', bg="lightblue")
audio_radio.pack(side=tk.LEFT)

text_var = tk.StringVar()

text_label = tk.Label(root, text="Enter Message to Encode:", bg="lightblue")
text_label.pack(padx=10, pady=5)

text_entry = tk.Entry(root, textvariable=text_var, width=50)
text_entry.pack(padx=10, pady=5)

# File selection for image and audio
image_path_var = tk.StringVar()
audio_path_var = tk.StringVar()

image_button = tk.Button(root, text="Browse Image", command=browse_image)
image_button.pack(padx=10, pady=5)

audio_button = tk.Button(root, text="Browse Audio", command=browse_audio)
audio_button.pack(padx=10, pady=5)

# Buttons for encoding, decoding, and reset
encode_button = tk.Button(root, text="Encode", command=encode, bg="gold")
encode_button.pack(padx=10, pady=5)

decode_button = tk.Button(root, text="Decode", command=decode, bg="gold")
decode_button.pack(padx=10, pady=5)

reset_button = tk.Button(root, text="Reset", command=reset, bg="red", fg="white")
reset_button.pack(padx=10, pady=5)

# Encrypted message display box
encrypted_message_display = tk.Text(root, height=5, width=50, wrap=tk.WORD, state=tk.DISABLED)
encrypted_message_display.pack(padx=10, pady=5)

# Decrypted message display area
decrypted_message_display = tk.Text(root, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
decrypted_message_display.pack(padx=10, pady=5)

root.mainloop()
