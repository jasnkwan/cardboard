import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

if __name__ == "__main__":

    # Configuration
    SERIAL_PORT = '/dev/tty.usbmodem11303'  # Replace with your serial port
    BAUD_RATE = 115200
    BUFFER_SIZE = 4 * 64  # Buffer size for uint32 (4 bytes per value)
    SAMPLING_RATE = 84000  # Sampling rate in Hz
    SIGNAL_FREQUENCY = 500  # Frequency of the sine wave in Hz
    PLOT_WINDOW = 3 / SIGNAL_FREQUENCY  # Duration to display 3 cycles

    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=120)  # Replace with your serial port and baudrate
    print(f"Connected to serial port.")

    # Calculate the number of samples to display in the plot window
    num_samples = int(PLOT_WINDOW * SAMPLING_RATE)

    # Initialize data storage
    data_buffer = np.zeros(num_samples, dtype=np.float32)

    # Create the figure and axis
    fig, ax = plt.subplots()
    line, = ax.plot(np.linspace(0, PLOT_WINDOW, num_samples), data_buffer)
    ax.set_xlim(0, PLOT_WINDOW)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Live Data Plot")

    def update(frame):
        global data_buffer

        # Read data from the serial port
        buf = bytearray(BUFFER_SIZE)
        n = ser.readinto(buf)
        if n > 0:
            # Convert to uint32 and normalize
            uint32_data = np.frombuffer(buf[:n], dtype=np.uint32)

            # Extract left channel data (assuming interleaved left and right)
            left_channel_data = uint32_data[::2]

            normalized_data = (left_channel_data.astype(np.float32) / (2**31)) - 1.0

            # Update the data buffer
            num_new_samples = len(normalized_data)
            if num_new_samples > 0:
                data_buffer = np.roll(data_buffer, -num_new_samples)
                data_buffer[-num_new_samples:] = normalized_data

        # Update the plot
        line.set_ydata(data_buffer)
        return line,

    # Set up the animation
    ani = FuncAnimation(fig, update, interval=100, blit=True)

    # Show the plot
    try:
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print(f"Closed serial port.")

    '''
    done = False

    while not done:
        # Read up to buffer_size bytes into the buffer
        n = ser.readinto(buf)

        # Process the received data (e.g., convert to a bytes object, parse, etc.)
        #data = bytes(buf[:n])  # Convert bytearray to bytes object
        #print(f"data={data}")

        data_array = np.frombuffer(buf[:n], dtype=np.uint32)  # Example with uint8
        #print(f"{data_array}")

        normalized_data = (data_array.astype(np.float32) / (2**31)) - 1.0
        print(f"{normalized_data}")

    # Close the serial port
    ser.close()

    print(f"Closed serial port.")
    '''