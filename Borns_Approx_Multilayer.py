""" This program reads a flex history file (by calling a function from another file) and is able to compute different signal values from PZflex models. """

import numpy as np
import matplotlib.pyplot as plt
from fileio import read_flxhst
from scipy import signal

TargFileA = '123457.flxhst'
TransmitA = '123456_l7.flxhst'

TargFileB = '1234567.flxhst' # phase- and scale-shifted, 'target' file
TransmitB = '123456_l7.flxhst'
file_list = [TargFileA, TargFileB, TransmitA, TransmitB]

labelA = '123457'
labelB = '1234567'
labeltransA = 'No Reflection'
labeltransB = 'No Reflection'
graph_title = 'Tester'

max_time = 6e-6  # second peak ends near .192e-6
elec = 35
Targ_A_reflection_start = 400  # ns
Targ_A_reflection_end = 951  # 400

'''   COMPARISON OPTIMIZATION SWITCHES   '''
USE_SCALE_OPTIMIZATION = False
scale_estimate = 1
USE_PHASE_OPTIMIZATION = False
target_shift_estimate = 0  # indices (approximately .85ns)
PLOT_DECONVOLVE = False
PLOT_TRANSMISSION = False
PLOT_RAW_SIGNALS = False
PLOT_SIGNAL = False
PLOT_SUBTRACTION_DIAGRAM = False
PLOT_PHASE = False
PLOT_SCALE = False
PLOT_CONTRAST = True
PLOT_ISO_WAVEFORM = False

'''   Target File A   '''
filedata1 = read_flxhst(TargFileA)
records1 = filedata1['records']
timelist1 = list(filedata1['times'])
timestep1 = filedata1['tstep']
test_time_inds1 = [timelist1.index(i) for i in timelist1 if i <= max_time]  # pulls the indices for timepoints
max_time_index1 = max(test_time_inds1)
test_times1 = [i * 1e9 for i in timelist1 if i <= max_time]
ptl1 = range(2, len(records1))  # point index list
TarglistA = [records1[x][13] for x in ptl1]  # collects currents of each RX line
TarglistA = [[x * 1e6 for x in indiv_elec] for indiv_elec in TarglistA]
TarglistA = [x[:len(test_times1)] for x in TarglistA]  # shorten to the length of the timelist

'''   Target File B   '''
filedata2 = read_flxhst(TargFileB)
records2 = filedata2['records']
timelist2 = list(filedata2['times'])
timestep2 = filedata2['tstep']
test_time_inds2 = [timelist2.index(i) for i in timelist2 if i <= max_time]  # pulls the indices for timepoints
max_time_index2 = max(test_time_inds2)
test_times2 = [i * 1e9 for i in timelist2 if i <= max_time]
ptl2 = range(2, len(records2))  # point index list
TarglistB = [records2[x][13] for x in ptl2]
TarglistB = [[x * 1e6 for x in indiv_elec] for indiv_elec in TarglistB]
TarglistB = [x[:len(test_times2)] for x in TarglistB]  # shorten to the length of the timelist

'''   Transmission A   '''
filedata3 = read_flxhst(TransmitA)
records3 = filedata3['records']
timelist3 = list(filedata3['times'])
timestep3 = filedata2['tstep']
test_time_inds3 = [timelist3.index(i) for i in timelist3 if i <= max_time]  # pulls the indices for timepoints
max_time_index3 = max(test_time_inds3)
test_times3 = [i * 1e9 for i in timelist3 if i <= max_time]
ptl3 = range(2, len(records3))  # point index list
TransmitlistA = [records3[x][13] for x in ptl3]
TransmitlistA = [[x * 1e6 for x in indiv_elec] for indiv_elec in TransmitlistA]  # measured in MICROAMPS
TransmitlistA = [x[:len(test_times3)] for x in TransmitlistA]  # shorten to the length of the timelist

'''   Transmission B   '''
filedata4 = read_flxhst(TransmitB)
records4 = filedata4['records']
timelist4 = list(filedata4['times'])
timestep4 = filedata4['tstep']
test_time_inds4 = [timelist4.index(i) for i in timelist4 if i <= max_time]  # pulls the indices for timepoints
max_time_index4 = max(test_time_inds4)
test_times4 = [i * 1e9 for i in timelist4 if i <= max_time]
ptl4 = range(2, len(records4))  # point index list
TransmitlistB = [records4[x][13] for x in ptl4]
TransmitlistB = [[x * 1e6 for x in indiv_elec] for indiv_elec in TransmitlistB]  # measured in MICROAMPS
TransmitlistB = [x[:len(test_times4)] for x in TransmitlistB]  # shorten to the length of the timelist

''' SUBTRACT OUT TRANSMISSION SIGNAL '''
Targ_B_minus_transmit = []  # subtracting the transmitted perturbations from the reflection
for e in range(len(TarglistB)):
    zippo = list(zip(TarglistB[e], TransmitlistB[e]))  # (target, noreflect)
    subtraction_per_elec = [x[0] - x[1] for x in zippo]  # (target - transmit)
    Targ_B_minus_transmit.append(subtraction_per_elec)

Targ_A_minus_transmit = []  # subtracting the transmitted perturbations from the reflection
for e in range(len(TarglistA)):
    zippo = list(zip(TarglistA[e], TransmitlistA[e]))
    subtraction_per_elec = [x[0] - x[1] for x in zippo]
    Targ_A_minus_transmit.append(subtraction_per_elec)

# scale the targetted to match untargetted

'''   SHORTEN TO INITIAL REFLECTION   '''
Targ_A_reflection_start_index = [x for x in test_time_inds1 if (round(test_times1[x]) == Targ_A_reflection_start)][0]
Targ_A_reflection_end_index = [x for x in test_time_inds1 if (round(test_times1[x]) == Targ_A_reflection_end)][0]
Targ_A_reflection_times = test_times1[Targ_A_reflection_start_index:Targ_A_reflection_end_index]
Targ_A_minus_transmit_reflect = [x[Targ_A_reflection_start_index:Targ_A_reflection_end_index] for x in
                                 Targ_A_minus_transmit]
Targ_B_minus_transmit_reflect_unphased = [x[Targ_A_reflection_start_index:Targ_A_reflection_end_index] for x in
                                 Targ_B_minus_transmit]  # not phase shifted

'''   ISOLATED WAVEFORM   '''

Iso = []
for e in range(len(TarglistA)):
    zippo = list(zip(TarglistA[e],TransmitlistA[e]))
    Isolate_per_elec = [(x[0] - x[1]) for x in zippo]
    Iso.append(Isolate_per_elec)
    
Targ_B_minus_transmit
Targ_A_minus_transmit


'''   CALCULATE CONTRAST   '''
Target_A_contrast = []
for e in range(len(TarglistA)):
    zippo = list(zip(TarglistA[e], TransmitlistA[e]))
    contrast_per_elec = [(x[0] - x[1]) / (x[0] + x[1]) for x in zippo]
    Target_A_contrast.append(contrast_per_elec)
    
Target_B_contrast = []
for s in range(len(TarglistB)):
    zippo = list(zip(TarglistB[s], TransmitlistB[s]))
    contrast_per_elec = [(x[0] - x[1]) / (x[0] + x[1]) for x in zippo]
    Target_B_contrast.append(contrast_per_elec)

'''   FIND PHASE SHIFT   '''
def match_maxima_v4(untarg, targ):
    untarg_max_indices = signal.argrelextrema(np.asarray(untarg), np.greater)[0]
    targ_max_indices = signal.argrelextrema(np.asarray(targ), np.greater)[0]
    untarg_max_indices = [x for x in untarg_max_indices if (untarg[x] > 0.25)]
    targ_max_indices = [x for x in targ_max_indices if (targ[x] > 0.25)]
    for x in [targ_max_indices, untarg_max_indices]:
        for n in range(1, (len(x) - 1)):
            if (x[n] - x[n - 1] < 8):
                x_new = np.mean([x[n], x[n - 1]])
                x[n - 1] = x_new
                x.remove(x[n])
    #    if abs(untarg_max_indices[0] - targ_max_indices[0]) not in range(10):
    #        if (len(untarg_max_indices) > len(targ_max_indices)):
    #            untarg_max_indices = untarg_max_indices[1:]
    #        elif (len(untarg_max_indices) < len(targ_max_indices)):
    #            targ_max_indices = targ_max_indices[1:]
    shifts_max = [x[0] - x[1] for x in zip(targ_max_indices, untarg_max_indices)]
    shiftmean = np.mean(shifts_max)
    return shiftmean


if USE_PHASE_OPTIMIZATION == True:
    shift_list = []
    Targ_B_minus_transmit_reflect_temp = []
    Targ_B_reflection_times = Targ_A_reflection_times
    for electrode in range(len(TarglistA)):
        shift0 = match_maxima_v4(Targ_A_minus_transmit_reflect[electrode],
                                 Targ_B_minus_transmit_reflect_unphased[electrode])
        shift_list.append(shift0)
        shift0 = int(shift0)

        Targ_B_reflection_start_index = Targ_A_reflection_start_index + shift0  ### the following line (i think) overphase-shifts, so this cancels that out
        Targ_B_reflection_end_index = Targ_B_reflection_start_index + len(Targ_B_reflection_times)
        Targ_B_minus_transmit_reflect_temp.append(Targ_B_minus_transmit[electrode][Targ_B_reflection_start_index:Targ_B_reflection_end_index])
    Targ_B_minus_transmit_reflect = Targ_B_minus_transmit_reflect_temp
else:
    shift_list = []
    Targ_B_reflection_start_index = Targ_A_reflection_start_index + target_shift_estimate
    Targ_B_reflection_end_index = Targ_B_reflection_start_index + len(Targ_A_reflection_times)
    Targ_B_reflection_times = test_times2[Targ_A_reflection_start_index:Targ_A_reflection_end_index]
    Targ_B_minus_transmit_reflect = [x[Targ_B_reflection_start_index:Targ_B_reflection_end_index] for x in
                                     Targ_B_minus_transmit]

'''   COLLECT AMPLITUDE INFO '''  # JUST BECAUSE WE CAN
amp_list = []
for electrode in range(len(TarglistA)):
    amp = max(Targ_B_minus_transmit_reflect[electrode])
    amp_list.append(amp)

'''   SCALE EACH ELECTRODE   '''
def compare_reflection(scale, untarg,
                       targ):  # takes two signal lists and a scalar, and returns a comparative value of the error between the two.
    scaled_targ = [x * scale for x in targ]
    difference = [abs(x[1] - x[0]) for x in
                  list(zip(untarg, scaled_targ))]  # absolute value measures total error, not equated pos/neg error
    difference = np.mean(difference)
    return difference


'''   MINIMIZE SCALAR DIFFERENCE FOR EACH ELECTRODE   '''
if USE_SCALE_OPTIMIZATION == True:
    scale_list = []
    for electrode in range(len(TarglistA)):
        diff_list = []
        test_range = np.arange(0.1, 6.00, 0.001)
        for scale_est in test_range:
            diff_list.append(compare_reflection(scale_est, Targ_A_minus_transmit_reflect[electrode],
                                                Targ_B_minus_transmit_reflect[electrode]))
        indexo = diff_list.index(min(diff_list))
        scale_best = test_range[indexo]
        scale_list.append(scale_best)
else:
    scale_list = [scale_estimate for x in range(len(TarglistA))]

# scaled_wtarget_minus_transmit_reflect = [[x*scale for x in displist] for displist in wtarget_minus_transmit_reflect]

'''   SCALE THE TARGET   '''
scaled_Targ_B_minus_transmit_reflect = []
for index in range(len(Targ_B_minus_transmit_reflect)):
    scaled_elec = [x * scale_list[index] for x in Targ_B_minus_transmit_reflect[index]]
    scaled_Targ_B_minus_transmit_reflect.append(scaled_elec)

'''   Calculate Error   '''
def calc_error(untarg, targ):
    numerator_list = [2 * (x[0] - x[1]) for x in zip(untarg, targ)]  # 2*(untarg-targ)
    denominator_list = [abs(x[0]) + abs(x[1]) for x in zip(untarg, targ)]  # |untarg| + |targ|
    for index, denom in enumerate(denominator_list):
        if denom == 0:
            denominator_list[index] = 1
    error_list = [x[0] / x[1] for x in zip(numerator_list, denominator_list)]
    return np.mean(error_list)


error_list = []
for electrode in range(len(TarglistA)):
    error = calc_error(Targ_A_minus_transmit_reflect[electrode], scaled_Targ_B_minus_transmit_reflect[electrode])
    error_list.append(error)

'''   PLOT THE ARRAY   '''

if PLOT_SIGNAL == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    plt.plot(Targ_A_reflection_times, Targ_A_minus_transmit_reflect[elec], label=labelA + '; Electrode ' + str(elec))
    plt.plot(Targ_B_reflection_times, scaled_Targ_B_minus_transmit_reflect[elec],
             label=labelB + '; Electrode ' + str(elec))
    plt.ylabel('Current (uA)')
    plt.title(graph_title)
    plt.legend()
    plt.grid()

'''   DECONVOLVE   '''
if PLOT_DECONVOLVE == True:
    targ_fft = np.fft.fft(scaled_Targ_B_minus_transmit_reflect[elec])
    transmit_fft = np.fft.fft(TransmitlistB[elec])
    transmit_fft = transmit_fft[:len(targ_fft):1]
    impulse_fft = [x[0] / x[1] for x in list(zip(targ_fft, transmit_fft))]
    impulse = np.fft.ifft(impulse_fft)
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    plt.plot(Targ_B_reflection_times, impulse, label='Impulse Response: Electrode ' + str(elec))
    plt.legend()
    plt.grid()

if PLOT_PHASE == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    shift_ylist = [y * timestep1 * 1e9 for y in shift_list]  # nanoseconds
    plt.plot(shift_ylist)
    plt.xlabel('Electrode Number')
    plt.ylabel('Phase Shift (ns)')
    plt.title('Targeted Reflection Phase Shift (vs. Untargeted Reflection): ' + labelB)
    plt.grid()

if PLOT_SCALE == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    scale_ylist = [1 / x for x in scale_list]
    plt.plot(scale_ylist)
    plt.xlabel('Electrode Number')
    plt.ylabel('Scale Relative to Untargeted Reflection (ns)')
    plt.title('Targeted Reflection Scale (vs. Untargeted Reflection): ' + labelA)

if PLOT_TRANSMISSION == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    plt.plot(test_times3, TransmitlistA[elec], label=labeltransA)
    plt.plot(test_times4, TransmitlistB[elec], label=labeltransB)
    plt.xlabel('Time (ns)')
    plt.ylabel('Current(uA)')

if PLOT_RAW_SIGNALS == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    plt.plot(test_times1, TarglistA[elec], label=labelA)
    plt.plot(test_times2, TarglistB[elec], label=labelB)
    plt.xlabel('Time (ns)')
    plt.ylabel('Current(uA)')
    plt.legend()
    plt.grid()

if PLOT_SUBTRACTION_DIAGRAM == True:
    plt.subplot(3, 1, 1)
    plt.plot(test_times3, TransmitlistA[elec], label='No Reflection; Electrode ' + str(elec))
    plt.title(graph_title)
    plt.legend()
    plt.grid()
    
    plt.subplot(3, 1, 2)
    plt.plot(test_times1, TarglistA[elec], label='With Reflection; Electrode ' + str(elec))
    plt.ylabel('Current (uA)')
    plt.legend()
    plt.grid()

    plt.subplot(3, 1, 3)
    plt.plot(test_times2, Targ_A_minus_transmit[elec], label='Reflected Minus Transmitted; Electrode ' + str(elec))
    plt.xlabel('time (ns)')
    plt.legend()
    plt.grid()
    
    plt.figure(figsize=(14, 14))
    
if PLOT_CONTRAST == True:
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(14, 14))
    plt.plot(test_times1, Target_A_contrast[elec], label=labelA)
    plt.plot(test_times2, Target_B_contrast[elec], label=labelB)
    plt.xlabel('Time (ns)')
    plt.ylabel('Contrast')
    plt.legend()
    plt.grid()