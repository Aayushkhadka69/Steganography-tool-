import unittest
from steganography_tool import encode_image, decode_image, encode_audio, decode_audio

class TestSteganographyTool(unittest.TestCase):

    # Set up test files (audio and image)
    def setUp(self):
        # Paths to test files (assumed to be in the same directory as the test file)
        self.test_image = 'test_image.png'  # Path to test image
        self.test_audio = 'test_audio.wav'  # Path to test audio
        self.encoded_image = 'encoded_image.png'  # Output encoded image
        self.encoded_audio = 'encoded_audio.wav'  # Output encoded audio
        self.message = "This is a secret message"

    # Test encoding and decoding an image
    def test_encode_decode_image(self):
        print("Testing image encoding and decoding...")
        # Encode the message into the image
        encode_image(self.test_image, self.message, self.encoded_image)

        # Decode the message from the encoded image
        decoded_message = decode_image(self.encoded_image)
        
        # Check if the decoded message is the same as the original message
        self.assertEqual(decoded_message, self.message)
        print("Image encoding/decoding test passed.")

    # Test encoding and decoding an audio file
    def test_encode_decode_audio(self):
        print("Testing audio encoding and decoding...")
        # Encode the message into the audio file
        encode_audio(self.test_audio, self.message, self.encoded_audio)

        # Decode the message from the encoded audio
        decoded_message = decode_audio(self.encoded_audio)
        
        # Check if the decoded message is the same as the original message
        self.assertEqual(decoded_message, self.message)
        print("Audio encoding/decoding test passed.")

if __name__ == '__main__':
    unittest.main()
