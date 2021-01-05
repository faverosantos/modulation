import matplotlib.pyplot as plt
import numpy as np
from numpy import random
from scipy.fft import fft, fftfreq

# References
# https://blogs.zhinst.com/mehdia/2019/11/25/how-to-generate-qam-signaling-with-the-hdawg-arbitrary-waveform-generator/

class Defines:

    # Sampling frequency
    FS = 100E9

    # Number of samples
    N_SAMPLES = 1000


def export_as_pwl(name, time, amplitude):
    file = open(name,"w")

    for local_index in range(0, len(amplitude)):
        file.write(str(time[local_index]))
        file.write(" ")
        file.write(str(amplitude[local_index]))
        file.write("\n")
    file.close()


# Reference: https://en.wikipedia.org/wiki/RC_circuit
def channel_model(vin, R, C, noise_level, skew_level):

    if skew_level != 0:
        level = 0
        previous_level = 0
        for i in range(len(vin)):
            level = vin[i]
            if i == 0:
                previous_level = level

            if level != previous_level: #add random skew
                skew_index = random.randint(skew_level)
                skew_position = random.randint(2)

                if skew_position == 1:
                    for j in range(i-skew_index, i):
                        vin[j] = vin[i]
                elif skew_position == 0:
                    for j in range(i, i+skew_index):
                        vin[j] = vin[i-1]

            previous_level = level

    if noise_level != 0: #add random noise
        for i in range(len(vin)):
            vin[i] += random.uniform(-noise_level, noise_level)



    t = np.arange(1,len(vin)+1)
    tau = R * C
    #print("tau: " + str(tau))
    ri = (1/tau) * np.exp(- t / tau)
    #plt.plot(ri)
    vout = np.convolve(ri, vin)
    vout = vout[0:len(vin)]

    return vout

def generate_QAM_signal(carrier_frequency, depth, symbol_duration):

    [i_t, q_t] = generate_QAM_symbols(depth, symbol_duration)

    [position, sin_t] = generate_sine_wave(carrier_frequency, 0, 0, 1, len(i_t))
    [position, cos_t] = generate_sine_wave(carrier_frequency, np.pi / 2, 0, 1, len(q_t))

    time = position / Defines.FS
    print("Duration of the signal:", str((time[-1] - time[0])*1000), "ms")
    s_t = i_t * sin_t + q_t * cos_t

    return [time, s_t]


def fft_of(signal):

    n = len(signal)
    f_amplitude = fft(signal)
    frequency = fftfreq(n, 1/Defines.FS)[:n// 2]

    h_amplitude = 2.0 / n * np.abs(f_amplitude[0:n // 2])

    return [frequency, h_amplitude]

def generate_QAM_symbols(depth, symbol_duration):

    M = depth
    x = np.ones(int(symbol_duration*Defines.FS))
    wi = np.ones(int(symbol_duration*Defines.FS))
    wq = np.ones(int(symbol_duration*Defines.FS))

    wiAcc = []
    wqAcc = []

    for i in range(-(M - 1), M, 2):
        for q in range(-(M - 1), M, 2):
            wi = (i / M) * x
            wq = (q / M) * x
            wiAcc = [*wiAcc, *wi]
            wqAcc = [*wqAcc, *wq]

    return [wiAcc, wqAcc]

# Generates a sine wave
# Inputs: frequency (Hz), phase (rad/s), offset (V), amplitude (V), size (amount of samples)
def generate_sine_wave(frequency, phase, offset, amplitude, size):
    w = 2 * np.pi * frequency
    x = np.arange(size)

    y = offset + amplitude*np.sin(w * x / Defines.FS + phase)

    return [x, y]

def generate_eye_diagram(data, bit_duration):

    level = 0
    previous_level = 0
    rising_index = 0
    falling_index = 0
    THRESHOLD = 0.5

    for i in range(len(data)):
        level = data[i]
        if i == 0:
            previous_level = level

        if level > previous_level + THRESHOLD: # rising edge
            rising_index = i

        elif level < previous_level - THRESHOLD: #falling edge
            falling_index = i


        #TODO continuar aqui, tem que preencher o buffer com as amostras corretas
        if rising_index != falling_index:
            eye[i, 0:bit_duration] = not bit_value
            eye[i, bit_duration:2*bit_duration] = buffer[j, 0:bit_duration]
            eye[i, 2*bit_duration:3 * bit_duration] = not bit_value

        previous_level = level




    #buffer = np.zeros((int(len(data)/bit_duration), bit_duration))
    #eye = np.zeros((int(len(data) / bit_duration), 3*bit_duration))

    #j = 0

    #for i in range(0, len(data), bit_duration):
    #    buffer[j, 0:bit_duration] = data[i:bit_duration+j*bit_duration]
    #    bit_value = buffer[j, bit_duration-1] #np.ceil(np.average(buffer[j, 0:bit_duration]))

    #    eye[j, 0:bit_duration] = not bit_value
    #    eye[j, bit_duration:2*bit_duration] = buffer[j, 0:bit_duration]
    #    eye[j, 2*bit_duration:3 * bit_duration] = not bit_value

    #    j = j + 1

    return eye

def generate_random_word(size, bit_duration):

    #word = np.concatenate([np.zeros(size), np.ones(size)])

    word = []

    for i in range(size):
        bit = random.randint(2)
        bit_vector = np.ones(int(bit_duration)) * bit

        word = [*word, *bit_vector]



    return word

if __name__ == "__main__":

    carrier_frequency = 2.4E9
    symbol_duration = 3.6/(1E6)

    #[time, s_t] = generate_QAM_signal(carrier_frequency, 2, symbol_duration)
    #plt.plot(time, s_t)
    #plt.show()

    #[frequency, h_amplitude] = fft_of(s_t)

    #plt.plot(frequency, h_amplitude)
    #plt.show()


    #vin = np.concatenate([np.zeros(400), np.ones(200), np.zeros(4000)])
    #plt.plot(vin)
    #vout = channel_model(vin, 50, 10)

    BIT_DURATION = 10
    word = generate_random_word(10, BIT_DURATION)
    plt.plot(word)

    NOISE_LEVEL = 0.01
    SKEW_LEVEL = BIT_DURATION/2
    vout = channel_model(word, 20, 0.1, NOISE_LEVEL, SKEW_LEVEL)
    plt.plot(vout)
    plt.show()


    eye = generate_eye_diagram(word, BIT_DURATION)
    for i in range(0, len(eye)):
        plt.plot(eye[i,:])
    plt.show()


    eye = generate_eye_diagram(vout, BIT_DURATION)
    for i in range(0, len(eye)):
        plt.plot(eye[i,:])
    plt.show()



