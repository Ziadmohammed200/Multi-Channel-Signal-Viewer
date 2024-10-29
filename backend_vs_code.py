import requests
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import subprocess

# Function to stream audio from the URL using ffmpeg
def stream_audio(url):
    process = subprocess.Popen(
        ['ffmpeg', '-i', url, '-f', 'wav', '-'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    return process

# Function to process and plot the audio signal
def plot_audio_signal(audio_process):
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    buffer_size = 1024
    buffer = np.zeros(buffer_size)
    x = np.arange(buffer_size)  # Time points (will be updated)
    line, = ax.plot(x, buffer)
    plt.ylim(-1, 1)
    plt.show()

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        if indata.shape[0] == buffer_size:
            line.set_ydata(indata[:, 0])
            fig.canvas.draw()
            fig.canvas.flush_events()

    try:
        with sd.InputStream(samplerate=44100, channels=1, callback=audio_callback):
            time_index = 0
            while plt.fignum_exists(fig.number):  # Check if the plot window is still open
                data = audio_process.stdout.read(buffer_size * 2)  # Read buffer_size * 2 bytes to get buffer_size samples
                if not data:
                    break
                audio_data = np.frombuffer(data, dtype=np.int16) / 32768.0
                if audio_data.shape[0] == buffer_size:
                    buffer = np.append(buffer, audio_data)[-buffer_size:]  # Keep the last buffer_size samples
                    time_index += buffer_size

                    # Update the x-axis so that time increases from left to right
                    new_time = np.arange(time_index - buffer_size, time_index)
                    line.set_xdata(new_time)  # Update time points on x-axis
                    line.set_ydata(buffer)    # Update signal values on y-axis
                    ax.set_xlim(time_index - buffer_size, time_index)  # Shift the x-axis
                    fig.canvas.draw()
                    fig.canvas.flush_events()
    except KeyboardInterrupt:
        print("Stream stopped by user")
    finally:
        # Ensure the plot window closes and the audio process is terminated
        audio_process.terminate()  # Stop the ffmpeg process
        audio_process.stdout.close()  # Close the stdout

# Main function
def main():
    url = "https://s44.myradiostream.com/9204/listen.mp3"
    audio_stream = stream_audio(url)
    plot_audio_signal(audio_stream)

if __name__ == "__main__":
    main()
